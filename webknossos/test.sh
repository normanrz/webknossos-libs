#!/usr/bin/env bash
set -eEuo pipefail

export WK_TOKEN=1b88db86331a38c21a0b235794b9e459856490d70408bcffb767f64ade0f83d2bdb4c4e181b9a9a30cdece7cb7c65208cc43b6c1bb5987f5ece00d348b1a905502a266f8fc64f0371cd6559393d72e031d0c2d0cabad58cccf957bb258bc86f05b5dc3d4fff3d5e3d9c0389a6027d861a21e78e3222fb6c5b7944520ef21761e
export WK_URL=http://localhost:9000
export DOCKER_TAG=master__16748

if [ $# -eq 1 ] && [ "$1" = "--refresh-snapshots" ]; then
    if ! curl -sf localhost:9000/api/health; then
        echo "Using docker-compose setup with the docker tag $DOCKER_TAG"
        echo "  To change this, please update DOCKER_TAG in test.sh"

        WK_DOCKER_DIR="tests"
        pushd $WK_DOCKER_DIR > /dev/null
        docker-compose pull webknossos
        # TODO: either remove pg/db before starting or run tools/postgres/apply_evolutions.sh
        USER_UID=$(id -u) USER_GID=$(id -g) docker-compose up -d --no-build webknossos
        stop_wk () {
            ARG=$?
            pushd $WK_DOCKER_DIR > /dev/null
            docker-compose down
            popd > /dev/null
            exit $ARG
        }
        trap stop_wk EXIT
        while ! curl -sf localhost:9000/api/health; do
            sleep 5
        done
        OUT=$(docker-compose exec webknossos tools/postgres/prepareTestDB.sh 2>&1) || echo "$OUT"
        popd > /dev/null
    else
        echo "Using the already running local webknossos setup at localhost:9000"
    fi

    rm -rf tests/cassettes
    rm -rf tests/**/cassettes

    if ! curl -s -H "X-Auth-Token: $WK_TOKEN" localhost:9000/api/user | grep user_A@scalableminds.com > /dev/null; then
        echo "The login user user_A@scalableminds.com could not be found or changed."
        echo "Please ensure that the test-db is prepared by running this in the webknossos repo:"
        echo "tools/postgres/prepareTestDB.sh"
        exit 1
    fi

    WK_ORG_VERSION="$(curl -s https://webknossos.org/api/buildinfo | tr ',"' "\n" | sed -n '/version/{n;n;p;q;}')"
    LOCAL_VERSION="$(curl -s http://localhost:9000/api/buildinfo | tr ',"' "\n" | sed -n '/version/{n;n;p;q;}')"

    if [ "$WK_ORG_VERSION" != "$LOCAL_VERSION" ]; then
        echo "The local webknossos version is $LOCAL_VERSION, differing from the webknossos.org version $WK_ORG_VERSION"
    fi

    # Note that pytest should be executed via `python -m`, since
    # this will ensure that the current directory is added to sys.path
    # (which is standard python behavior). This is necessary so that the imports
    # refer to the checked out (and potentially modified) code.
    poetry run python -m pytest --record-mode once
else
    poetry run python -m pytest --block-network
fi
