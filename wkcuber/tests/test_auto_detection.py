from wkcuber.converter import ImageStackConverter, KnossosConverter
from os.path import sep

TEST_PREFIXES = ["", "/", f"../"]


def fix_sep(path: str) -> str:
    return path.replace("/", sep)


def test_tiff_dataset_name_and_layer_name_detection() -> None:
    for prefix in TEST_PREFIXES:

        # test if ds name and layer name are correctly detected
        converter = ImageStackConverter()
        converter.source_files = [
            fix_sep(f"{prefix}test/color/001.tif"),
            fix_sep(f"{prefix}test/color/002.tif"),
            fix_sep(f"{prefix}test/color/003.tif"),
        ]
        (
            dataset_name,
            layer_path_to_layer_name,
        ) = converter.detect_dataset_name_and_layer_path_to_layer_name()
        assert dataset_name == "test"
        assert len(layer_path_to_layer_name) == 1
        assert list(layer_path_to_layer_name)[0] == fix_sep(f"{prefix}test/color")
        assert list(layer_path_to_layer_name.values())[0] == "color"

        # test if in subfolder
        converter = ImageStackConverter()
        converter.source_files = [
            fix_sep(f"{prefix}superfolder/test/color/001.tif"),
            fix_sep(f"{prefix}superfolder/test/color/002.tif"),
            fix_sep(f"{prefix}superfolder/test/color/003.tif"),
        ]
        (
            dataset_name,
            layer_path_to_layer_name,
        ) = converter.detect_dataset_name_and_layer_path_to_layer_name()
        assert dataset_name == "test"
        assert len(layer_path_to_layer_name) == 1
        assert list(layer_path_to_layer_name)[0] == fix_sep(
            f"{prefix}superfolder/test/color"
        )
        assert list(layer_path_to_layer_name.values())[0] == "color"

        # test for multiple layers
        converter = ImageStackConverter()
        converter.source_files = [
            fix_sep(f"{prefix}test/color/001.tif"),
            fix_sep(f"{prefix}test/color/002.tif"),
            fix_sep(f"{prefix}test/color/003.tif"),
            fix_sep(f"{prefix}test/segmentation/001.tif"),
            fix_sep(f"{prefix}test/segmentation/002.tif"),
            fix_sep(f"{prefix}test/segmentation/003.tif"),
        ]
        (
            dataset_name,
            layer_path_to_layer_name,
        ) = converter.detect_dataset_name_and_layer_path_to_layer_name()
        assert dataset_name == "test"
        assert len(layer_path_to_layer_name) == 2
        assert fix_sep(f"{prefix}test/color") in layer_path_to_layer_name.keys()
        assert fix_sep(f"{prefix}test/segmentation") in layer_path_to_layer_name.keys()
        assert "color" in layer_path_to_layer_name.values()
        assert "segmentation" in layer_path_to_layer_name.values()

        # test if in single folder and folder name is layer name
        converter = ImageStackConverter()
        converter.source_files = [
            fix_sep(f"{prefix}color/001.tif"),
            fix_sep(f"{prefix}color/002.tif"),
            fix_sep(f"{prefix}color/003.tif"),
        ]
        (
            dataset_name,
            layer_path_to_layer_name,
        ) = converter.detect_dataset_name_and_layer_path_to_layer_name()
        assert dataset_name == "dataset"
        assert len(layer_path_to_layer_name) == 1
        assert list(layer_path_to_layer_name)[0] == fix_sep(f"{prefix}color")
        assert list(layer_path_to_layer_name.values())[0] == "color"

        # test if in single folder and folder name is ds name
        converter = ImageStackConverter()
        converter.source_files = [
            fix_sep(f"{prefix}test_dataset/001.tif"),
            fix_sep(f"{prefix}test_dataset/002.tif"),
            fix_sep(f"{prefix}test_dataset/003.tif"),
        ]
        (
            dataset_name,
            layer_path_to_layer_name,
        ) = converter.detect_dataset_name_and_layer_path_to_layer_name()
        assert dataset_name == "test_dataset"
        assert len(layer_path_to_layer_name) == 1
        assert list(layer_path_to_layer_name)[0] == fix_sep(f"{prefix}test_dataset")
        assert list(layer_path_to_layer_name.values())[0] == "color"

        # test if single file in folder
        converter = ImageStackConverter()
        converter.source_files = [fix_sep(f"{prefix}test_dataset/brain.tif")]
        (
            dataset_name,
            layer_path_to_layer_name,
        ) = converter.detect_dataset_name_and_layer_path_to_layer_name()
        assert dataset_name == "test_dataset"
        assert len(layer_path_to_layer_name) == 1
        assert list(layer_path_to_layer_name)[0] == fix_sep(
            f"{prefix}test_dataset/brain.tif"
        )
        assert list(layer_path_to_layer_name.values())[0] == "brain"

        # test if single file
        converter = ImageStackConverter()
        converter.source_files = [fix_sep(f"{prefix}brain.tif")]
        (
            dataset_name,
            layer_path_to_layer_name,
        ) = converter.detect_dataset_name_and_layer_path_to_layer_name()
        assert dataset_name == "brain"
        assert len(layer_path_to_layer_name) == 1
        assert list(layer_path_to_layer_name)[0] == fix_sep(f"{prefix}brain.tif")
        assert list(layer_path_to_layer_name.values())[0] == "color"

        # test for multiple files with no parent directory
        converter = ImageStackConverter()
        converter.source_files = [
            fix_sep(f"{prefix}001.tif"),
            fix_sep(f"{prefix}002.tif"),
        ]
        (
            dataset_name,
            layer_path_to_layer_name,
        ) = converter.detect_dataset_name_and_layer_path_to_layer_name()
        assert dataset_name == "dataset"
        assert len(layer_path_to_layer_name) == 1
        assert list(layer_path_to_layer_name.keys())[0] == fix_sep(prefix)
        assert list(layer_path_to_layer_name.values())[0] == "color"


def test_knossos_dataset_name_and_layer_path_detection() -> None:
    for prefix in TEST_PREFIXES:

        # test if dataset name and layer name and mag are correct
        converter = KnossosConverter()
        converter.source_files = [
            fix_sep(
                f"{prefix}knossos/color/1/x0000/y0000/z0000/test_mag1_x0000_y0000_z0000.raw"
            ),
            fix_sep(
                f"{prefix}knossos/color/1/x0000/y0000/z0001/test_mag1_x0000_y0000_z0001.raw"
            ),
            fix_sep(
                f"{prefix}knossos/color/1/x0000/y0001/z0000/test_mag1_x0000_y0001_z0000.raw"
            ),
        ]
        dataset_name, layer_paths = converter.detect_dataset_and_layer_paths_with_mag()
        assert dataset_name == "knossos"
        assert len(layer_paths) == 1
        assert list(layer_paths.keys())[0] == fix_sep(f"{prefix}knossos/color")
        assert list(layer_paths.values())[0] == {"1"}

        # test if in subfolder
        converter = KnossosConverter()
        converter.source_files = [
            fix_sep(
                f"{prefix}superfolder/superfolder/knossos/color/1/x0000/y0000/z0000/test_mag1_x0000_y0000_z0000.raw"
            ),
        ]
        dataset_name, layer_paths = converter.detect_dataset_and_layer_paths_with_mag()
        assert dataset_name == "knossos"
        assert len(layer_paths) == 1
        assert list(layer_paths.keys())[0] == fix_sep(
            f"{prefix}superfolder/superfolder/knossos/color"
        )
        assert list(layer_paths.values())[0] == {"1"}

        # test for multiple layer
        converter = KnossosConverter()
        converter.source_files = [
            fix_sep(
                f"{prefix}knossos/color/1/x0000/y0000/z0000/test_mag1_x0000_y0000_z0000.raw"
            ),
            fix_sep(
                f"{prefix}knossos/segmentation/1/x0000/y0000/z0000/test_mag1_x0000_y0000_z0000.raw"
            ),
        ]
        dataset_name, layer_paths = converter.detect_dataset_and_layer_paths_with_mag()
        assert dataset_name == "knossos"
        assert len(layer_paths) == 2
        assert fix_sep(f"{prefix}knossos/color") in layer_paths.keys()
        assert fix_sep(f"{prefix}knossos/segmentation") in layer_paths.keys()
        assert all(map(lambda m: m == {"1"}, layer_paths.values()))

        # test if only layer folder given
        converter = KnossosConverter()
        converter.source_files = [
            fix_sep(
                f"{prefix}color/1/x0000/y0000/z0000/test_mag1_x0000_y0000_z0000.raw"
            ),
        ]
        dataset_name, layer_paths = converter.detect_dataset_and_layer_paths_with_mag()
        assert dataset_name == "dataset"
        assert len(layer_paths) == 1
        assert list(layer_paths.keys())[0] == fix_sep(f"{prefix}color")
        assert list(layer_paths.values())[0] == {"1"}

        # test if only mag folder given
        converter = KnossosConverter()
        converter.source_files = [
            fix_sep(f"{prefix}1/x0000/y0000/z0000/test_mag1_x0000_y0000_z0000.raw"),
        ]
        dataset_name, layer_paths = converter.detect_dataset_and_layer_paths_with_mag()
        assert dataset_name == "dataset"
        assert len(layer_paths) == 1
        assert list(layer_paths.keys())[0] == fix_sep(prefix)
        assert list(layer_paths.values())[0] == {"1"}

        # test if already in mag folder
        converter = KnossosConverter()
        converter.source_files = [
            fix_sep(f"{prefix}x0000/y0000/z0000/test_mag1_x0000_y0000_z0000.raw"),
        ]
        dataset_name, layer_paths = converter.detect_dataset_and_layer_paths_with_mag()
        assert dataset_name == "dataset"
        assert len(layer_paths) == 1
        assert list(layer_paths.keys())[0] == fix_sep(prefix)
        assert list(layer_paths.values())[0] == {""}

        # test if too short path gets detected
        converter = KnossosConverter()
        converter.source_files = [
            fix_sep(f"{prefix}y0000/z0000/test_mag1_x0000_y0000_z0000.raw"),
        ]
        assertion_error = False
        try:
            _, _ = converter.detect_dataset_and_layer_paths_with_mag()
        except AssertionError:
            assertion_error = True
        assert assertion_error

        # test for multiple mags
        converter = KnossosConverter()
        converter.source_files = [
            fix_sep(
                f"{prefix}knossos/color/2/x0000/y0000/z0000/test_mag1_x0000_y0000_z0000.raw"
            ),
            fix_sep(
                f"{prefix}knossos/color/4/x0000/y0000/z0000/test_mag1_x0000_y0000_z0000.raw"
            ),
        ]
        dataset_name, layer_paths = converter.detect_dataset_and_layer_paths_with_mag()
        assert dataset_name == "knossos"
        assert len(layer_paths) == 1
        assert list(layer_paths.keys())[0] == fix_sep(f"{prefix}knossos/color")
        assert list(layer_paths.values())[0] == {"2", "4"}
