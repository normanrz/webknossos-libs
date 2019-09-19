import numpy as np
import os

from wkcuber.cubing import ensure_wkw
from wkcuber.utils import WkwDatasetInfo, open_wkw
from wkcuber.metadata import (
    write_webknossos_metadata,
    refresh_metadata,
    read_datasource_properties,
    read_metadata_for_layer,
)


def test_element_class_convertion():
    test_wkw_path = os.path.join("testoutput", "test_metadata")
    prediction_layer_name = "prediction"
    prediction_wkw_info = WkwDatasetInfo(
        test_wkw_path, prediction_layer_name, np.float32, 1
    )
    ensure_wkw(prediction_wkw_info, num_channels=3)

    write_custom_layer(test_wkw_path, "prediction", np.float32, num_channels=3)
    write_webknossos_metadata(
        test_wkw_path,
        "test_metadata",
        [11.24, 11.24, 28],
        compute_max_id=True,
        exact_bounding_box={"topLeft": [0, 0, 0], "width": 4, "height": 4, "depth": 4},
    )
    write_custom_layer(test_wkw_path, "segmentation", np.float64, num_channels=1)
    write_custom_layer(test_wkw_path, "color", np.uint8, num_channels=3)

    refresh_metadata(test_wkw_path)

    check_element_class_of_layer(test_wkw_path, "prediction", "float", np.float32)
    check_element_class_of_layer(test_wkw_path, "segmentation", "double", np.float64)
    check_element_class_of_layer(test_wkw_path, "color", "uint24", np.uint8)


def check_element_class_of_layer(
    test_wkw_path, layer_name, expected_element_class, expected_dtype
):
    datasource_properties = read_datasource_properties(test_wkw_path)
    layer_to_check = None
    for layer in datasource_properties["dataLayers"]:
        if layer["name"] == layer_name:
            layer_to_check = layer

    assert (
        layer_to_check
    ), f"Did not find layer {layer_name} in datasource_properties.json."
    assert layer_to_check["elementClass"] == expected_element_class
    _, converted_dtype, _, _ = read_metadata_for_layer(test_wkw_path, layer_name)
    assert converted_dtype == expected_dtype


def write_custom_layer(target_path, layer_name, dtype, num_channels):
    data = (
        np.arange(4 * 4 * 4 * num_channels)
        .reshape((num_channels, 4, 4, 4))
        .astype(dtype)
    )
    prediction_wkw_info = WkwDatasetInfo(target_path, layer_name, dtype, 1)
    ensure_wkw(prediction_wkw_info, num_channels=num_channels)
    with open_wkw(prediction_wkw_info, num_channels=num_channels) as dataset:
        dataset.write(off=(0, 0, 0), data=data)


if __name__ == "__main__":
    test_element_class_convertion()
