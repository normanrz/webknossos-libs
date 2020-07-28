set -xe
cp -r testoutput/tiff testoutput/tiff_upsampling
rm -r testoutput/tiff_upsampling/color/1

python -m wkcuber.upsampling \
  --jobs 2 \
  --from_mag 2-2-2 \
  --target_mag 1-1-1 \
  --buffer_cube_size 1024 \
  --layer_name color \
  --interpolation_mode nearest \
  testoutput/tiff

python -m wkcuber.downsampling \
  --jobs 2 \
  --from_mag 1-1-1 \
  --max 2-2-2 \
  --buffer_cube_size 256 \
  --layer_name color \
  --interpolation_mode nearest \
  testoutput/tiff

python tests/scripts/compare_wkw.py \
  testoutput/tiff_upsampling/color/2 testdata/tiff_mag_2_reference/color/2
