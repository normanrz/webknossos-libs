import logging
import math
from argparse import Namespace
from glob import iglob
from shutil import rmtree
from os.path import join
from os import makedirs
from typing import Tuple
import os

import numpy as np

from wkw import wkw

from wkcuber import downsample_mag
from wkcuber.api.MagDataset import (
    MagDataset,
    WKMagDataset,
    TiffMagDataset,
    TiledTiffMagDataset,
    find_mag_path_on_disk,
)
from wkcuber.downsampling_utils import get_next_mag, parse_interpolation_mode, downsample_cube_job, \
    determine_buffer_edge_len, DEFAULT_EDGE_LEN, use_logging
from wkcuber.mag import Mag
from wkcuber.utils import DEFAULT_WKW_FILE_LEN, get_executor_for_args, cube_addresses, parse_cube_file_name


class Layer:

    COLOR_TYPE = "color"
    SEGMENTATION_TYPE = "segmentation"

    def __init__(self, name, dataset, dtype_per_channel, num_channels):
        self.name = name
        self.dataset = dataset
        self.dtype_per_channel = dtype_per_channel
        self.num_channels = num_channels
        self.mags = {}

        full_path = join(dataset.path, name)
        makedirs(full_path, exist_ok=True)

    def get_mag(self, mag) -> MagDataset:
        mag = Mag(mag).to_layer_name()
        if mag not in self.mags.keys():
            raise IndexError("The mag {} is not a mag of this layer".format(mag))
        return self.mags[mag]

    def delete_mag(self, mag):
        mag = Mag(mag).to_layer_name()
        if mag not in self.mags.keys():
            raise IndexError(
                "Deleting mag {} failed. There is no mag with this name".format(mag)
            )

        del self.mags[mag]
        self.dataset.properties._delete_mag(self.name, mag)
        # delete files on disk
        full_path = find_mag_path_on_disk(self.dataset.path, self.name, mag)
        rmtree(full_path)

    def _create_dir_for_mag(self, mag):
        mag = Mag(mag).to_layer_name()
        full_path = join(self.dataset.path, self.name, mag)
        makedirs(full_path, exist_ok=True)

    def _assert_mag_does_not_exist_yet(self, mag):
        mag = Mag(mag).to_layer_name()
        if mag in self.mags.keys():
            raise IndexError(
                "Adding mag {} failed. There is already a mag with this name".format(
                    mag
                )
            )

    def set_bounding_box(
        self, offset: Tuple[int, int, int], size: Tuple[int, int, int]
    ):
        self.set_bounding_box_offset(offset)
        self.set_bounding_box_size(size)

    def set_bounding_box_offset(self, offset: Tuple[int, int, int]):
        size = self.dataset.properties.data_layers["color"].get_bounding_box_size()
        self.dataset.properties._set_bounding_box_of_layer(
            self.name, tuple(offset), tuple(size)
        )
        for _, mag in self.mags.items():
            mag.view.global_offset = offset

    def set_bounding_box_size(self, size: Tuple[int, int, int]):
        offset = self.dataset.properties.data_layers["color"].get_bounding_box_offset()
        self.dataset.properties._set_bounding_box_of_layer(
            self.name, tuple(offset), tuple(size)
        )
        for _, mag in self.mags.items():
            mag.view.size = size

    def setup_mag(self, mag: Mag) -> None:
        raise NotImplemented

    def _initialize_mag_from_other_mag(self, new_mag_name, other_mag, compress):
        raise NotImplemented

    def downsample(
            self,
            from_mag: Mag,
            max_mag: Mag,
            interpolation_mode: str,
            compress: bool,
            scale: Tuple[float, float, float] = None,
            buffer_edge_len=None,
            args: Namespace = None,
    ):
        # if 'scale' is set, the data gets downsampled anisotropic

        # pad all existing mags if necessary
        # during each downsampling step, the data shape or offset of the new mag should never need to be rounded
        existing_mags = sorted([Mag(mag) for mag in self.mags.keys()])
        all_mags_after_downsampling = existing_mags.copy()
        cur_mag = get_next_mag(from_mag, scale)
        while cur_mag <= max_mag:
            all_mags_after_downsampling += [cur_mag]
            cur_mag = get_next_mag(cur_mag, scale)

        lowest_mag = all_mags_after_downsampling[-1].as_np()

        # calculate aligned offset and size for lowest mag
        offset_in_mag1 = self.dataset.properties.data_layers[self.name].get_bounding_box_offset()
        size_in_mag1 = self.dataset.properties.data_layers[self.name].get_bounding_box_size()
        offset_in_lowest_mag = offset_in_mag1 // all_mags_after_downsampling[-1].as_np()
        end_offset_in_lowest_mag = -((np.array(offset_in_mag1) + size_in_mag1) // -all_mags_after_downsampling[-1].as_np())  # ceil div
        # translate alignment into mag 1
        aligned_offset_in_mag1 = lowest_mag * offset_in_lowest_mag
        aligned_size_in_mag1 = lowest_mag * (end_offset_in_lowest_mag - offset_in_lowest_mag)

        # pad the existing mags
        for mag_name in existing_mags:
            mag = self.mags[mag_name.to_layer_name()]
            aligned_offset = aligned_offset_in_mag1 // mag_name.as_np()
            aligned_size = aligned_size_in_mag1 // mag_name.as_np()
            current_offset = mag.get_view().global_offset
            current_size = mag.get_view().size

            shape = list((self.num_channels,) + tuple(aligned_size))
            # pad (left + right) and (top + bottom) and (front + back)
            for i in range(0, 3):
                # pad left / top / front
                buffer_width = (np.array(current_offset) - aligned_offset)[i]
                if buffer_width > 0:
                    padding_shape = shape
                    padding_shape[i+1] = buffer_width
                    mag.write(data=np.zeros(padding_shape, dtype=mag.get_dtype()), offset=aligned_offset)
                # pad right / bottom / back
                buffer_width = ((aligned_offset + aligned_size) - (np.array(current_offset) + np.array(current_size)))[i]
                if buffer_width > 0:
                    padding_shape = shape
                    padding_shape[i+1] = buffer_width
                    right_offset = aligned_offset
                    right_offset[i] = current_offset[i] + current_size[i]
                    mag.write(data=np.zeros(padding_shape, dtype=mag.get_dtype()), offset=right_offset)

        interpolation_mode = parse_interpolation_mode(interpolation_mode, self.name)
        prev_mag = from_mag
        target_mag = get_next_mag(prev_mag, scale)

        while target_mag <= max_mag:
            assert prev_mag < target_mag
            assert target_mag.to_layer_name() not in self.mags

            prev_mag_ds = self.mags[prev_mag.to_layer_name()]

            mag_factors = [
                t // s for (t, s) in zip(target_mag.to_array(), prev_mag.to_array())
            ]

            # initialize the new mag
            target_mag_ds = self._initialize_mag_from_other_mag(target_mag, prev_mag_ds, compress)

            # Get target view
            target_mag_view = target_mag_ds.get_view(is_bounded=False)

            # perform downsampling
            with get_executor_for_args(args) as executor:
                voxel_count_per_cube = np.prod(prev_mag_ds._get_file_dimensions())
                job_count_per_log = math.ceil(1024 ** 3 / voxel_count_per_cube)  # log every gigavoxel of processed data

                if buffer_edge_len is None:
                    buffer_edge_len = determine_buffer_edge_len(prev_mag_ds.view) # DEFAULT_EDGE_LEN
                job_args = (
                    mag_factors,
                    interpolation_mode,
                    buffer_edge_len,
                    compress,
                    job_count_per_log,
                )
                prev_mag_ds.get_view().for_zipped_chunks(
                    # this view is restricted to the bounding box specified in the properties
                    downsample_cube_job,
                    target_view=target_mag_view,
                    job_args_per_chunk=job_args,
                    source_chunk_size=np.array(target_mag_ds._get_file_dimensions()) * mag_factors,
                    target_chunk_size=target_mag_ds._get_file_dimensions(),
                    executor=executor
                )

            logging.info("Mag {0} successfully cubed".format(target_mag))

            prev_mag = target_mag
            target_mag = get_next_mag(target_mag, scale)


class WKLayer(Layer):
    def add_mag(
        self, mag, block_len=None, file_len=None, block_type=None
    ) -> WKMagDataset:
        if block_len is None:
            block_len = 32
        if file_len is None:
            file_len = DEFAULT_WKW_FILE_LEN
        if block_type is None:
            block_type = wkw.Header.BLOCK_TYPE_RAW

        # normalize the name of the mag
        mag = Mag(mag).to_layer_name()

        self._assert_mag_does_not_exist_yet(mag)
        self._create_dir_for_mag(mag)

        self.mags[mag] = WKMagDataset.create(self, mag, block_len, file_len, block_type)
        self.dataset.properties._add_mag(self.name, mag, block_len * file_len)

        return self.mags[mag]

    def get_or_add_mag(
        self, mag, block_len=None, file_len=None, block_type=None
    ) -> WKMagDataset:
        # normalize the name of the mag
        mag = Mag(mag).to_layer_name()

        if mag in self.mags.keys():
            assert (
                block_len is None or self.mags[mag].header.block_len == block_len
            ), f"Cannot get_or_add_mag: The mag {mag} already exists, but the block lengths do not match"
            assert (
                file_len is None or self.mags[mag].header.file_len == file_len
            ), f"Cannot get_or_add_mag: The mag {mag} already exists, but the file lengths do not match"
            assert (
                block_type is None or self.mags[mag].header.block_type == block_type
            ), f"Cannot get_or_add_mag: The mag {mag} already exists, but the block types do not match"
            return self.get_mag(mag)
        else:
            return self.add_mag(mag, block_len, file_len, block_type)

    def setup_mag(self, mag):
        # This method is used to initialize the mag when opening the Dataset. This does not create e.g. the wk_header.

        # normalize the name of the mag
        mag = Mag(mag).to_layer_name()

        self._assert_mag_does_not_exist_yet(mag)

        with wkw.Dataset.open(
            find_mag_path_on_disk(self.dataset.path, self.name, mag)
        ) as wkw_dataset:
            wk_header = wkw_dataset.header

        self.mags[mag] = WKMagDataset(
            self, mag, wk_header.block_len, wk_header.file_len, wk_header.block_type
        )
        self.dataset.properties._add_mag(
            self.name, mag, wk_header.block_len * wk_header.file_len
        )

    def _initialize_mag_from_other_mag(self, new_mag_name, other_mag, compress):
        block_type = wkw.Header.BLOCK_TYPE_LZ4HC if compress else wkw.Header.BLOCK_TYPE_RAW
        return self.add_mag(new_mag_name, other_mag.block_len, other_mag.file_len, block_type)


class TiffLayer(Layer):
    def add_mag(self, mag) -> MagDataset:
        # normalize the name of the mag
        mag = Mag(mag).to_layer_name()

        self._assert_mag_does_not_exist_yet(mag)
        self._create_dir_for_mag(mag)

        self.mags[mag] = self._get_mag_dataset_class().create(
            self, mag, self.dataset.properties.pattern
        )
        self.dataset.properties._add_mag(self.name, mag)

        return self.mags[mag]

    def get_or_add_mag(self, mag) -> MagDataset:
        # normalize the name of the mag
        mag = Mag(mag).to_layer_name()

        if mag in self.mags.keys():
            return self.get_mag(mag)
        else:
            return self.add_mag(mag)

    def setup_mag(self, mag):
        # This method is used to initialize the mag when opening the Dataset. This does not create e.g. folders.

        # normalize the name of the mag
        mag = Mag(mag).to_layer_name()

        self._assert_mag_does_not_exist_yet(mag)

        self.mags[mag] = self._get_mag_dataset_class()(
            self, mag, self.dataset.properties.pattern
        )
        self.dataset.properties._add_mag(self.name, mag)

    def _get_mag_dataset_class(self):
        return TiffMagDataset

    def _initialize_mag_from_other_mag(self, new_mag_name, other_mag, compress):
        return self.add_mag(new_mag_name)


class TiledTiffLayer(TiffLayer):
    def _get_mag_dataset_class(self):
        return TiledTiffMagDataset

    def downsample(
            self,
            from_mag: Mag,
            max_mag: Mag,
            interpolation_mode: str,
            compress: bool,
            scale: Tuple[float, float, float] = None,
            buffer_edge_len=None,
            args: Namespace = None,
    ):
        raise NotImplemented
