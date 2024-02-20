import copy
import argparse
from unittest.mock import patch

import pytest

from turbo_turtle import _settings
from turbo_turtle import _abaqus_wrappers


abaqus_command = "/dummy/command/abaqus"

geometry_namespace_sparse = {
    "input_file": ["input_file"],
    "output_file": "output_file",
    "unit_conversion": 1.,
    "euclidean_distance": 1.,
    "planar": None,
    "model_name": "model_name",
    "part_name": [None],
    "delimiter": ",",
    "header_lines": 0,
    "revolution_angle": 360.,
    "y_offset": 0.,
    "rtol": None,
    "atol": None
}
geometry_namespace_full = copy.deepcopy(geometry_namespace_sparse)
geometry_namespace_full.update({
    "planar": True,
    "part_name": ["part_name"],
    "rtol": 1.e-9,
    "atol": 1.e-9
}),
geometry_expected_options_sparse = [
    "--input-file",
    "--output-file",
    "--unit-conversion",
    "--euclidean-distance",
    "--model-name",
    "--delimiter",
    "--header-lines",
    "--revolution-angle",
    "--y-offset"
]
geometry_unexpected_options_sparse = ["--planar", "--part-name", "--atol", "--rtol"]

cylinder_namespace = {
    "inner_radius": 1.,
    "outer_radius": 2.,
    "height": 1.,
    "output_file": "output_file",
    "model_name": "model_name",
    "part_name": "part_name",
    "revolution_angle": 360.,
    "y_offset": 0.
}
cylinder_expected_options = [
    abaqus_command,
    "--inner-radius",
    "--outer-radius",
    "--height",
    "--output-file",
    "--model-name",
    "--part-name",
    "--revolution-angle",
    "--y-offset"
]

sphere_namespace_sparse = {
    "inner_radius": 1.,
    "outer_radius": 2.,
    "output_file": "output_file",
    "input_file": None,
    "quadrant": "both",
    "revolution_angle": 360.,
    "y_offset": 0.,
    "model_name": "model_name",
    "part_name": "part_name",
}
sphere_namespace_full = copy.deepcopy(sphere_namespace_sparse)
sphere_namespace_full.update({"input_file": "input_file"}),
sphere_expected_options_sparse = [
    abaqus_command,
    "--inner-radius",
    "--outer-radius",
    "--output-file",
    "--quadrant",
    "--revolution-angle",
    "--y-offset",
    "--model-name",
    "--part-name",
]
sphere_unexpected_options_sparse = ["--input-file"]

partition_namespace_sparse = {
    "input_file": "input_file",
    "output_file": None,
    "center": (0., 0., 0.),
    "xvector": (0., 0., 0.),
    "zvector": (0., 0., 0.),
    "model_name": "model_name",
    "part_name": ["part_name"],
    "big_number": 0.
}
partition_namespace_full = copy.deepcopy(partition_namespace_sparse)
partition_namespace_full.update({"output_file": "output_file"}),
partition_expected_options_sparse = [
    abaqus_command,
    "--input-file",
    "--center",
    "--xvector",
    "--zvector",
    "--model-name",
    "--part-name",
    "--big-number"
]
partition_unexpected_options_sparse = ["--output-file"]

mesh_namespace_sparse = {
    "input_file": "input_file",
    "element_type": "element_type",
    "output_file": None,
    "model_name": "model_name",
    "part_name": "part_name",
    "global_seed": "global_seed"
}
mesh_namespace_full = copy.deepcopy(mesh_namespace_sparse)
mesh_namespace_full.update({"output_file": "output_file"}),
mesh_expected_options_sparse = [
    abaqus_command,
    "--input-file",
    "--element-type",
    "--model-name",
    "--part-name",
    "--global-seed"
]
mesh_unexpected_options_sparse = ["--output-file"]

merge_namespace_sparse = {
    "input_file": ["input_file"],
    "output_file": "output_file",
    "merged_model_name": "merged_model_name",
    "model_name": [None],
    "part_name": [None],
}
merge_namespace_full = copy.deepcopy(merge_namespace_sparse)
merge_namespace_full.update({
    "model_name": ["model_name"],
    "part_name": ["part_name"],
}),
merge_expected_options_sparse = [
    "--input-file",
    "--output-file",
    "--merged-model-name",
]
merge_unexpected_options_sparse = ["--model-name", "--part-name"]

export_namespace_sparse = {
    "input_file": "input_file",
    "model_name": "model_name",
    "part_name": ["part_name"],
    "element_type": [None],
    "destination": ".",
    "assembly": None
}
export_namespace_full = copy.deepcopy(export_namespace_sparse)
export_namespace_full.update({
    "element_type": ["element_type"],
    "assembly": True,
}),
export_expected_options_sparse = [
    "--input-file",
    "--model-name",
    "--part-name",
    "--destination"
]
export_unexpected_options_sparse = ["--element-type", "--assembly"]

image_namespace_sparse = {
    "input_file": "input_file",
    "output_file": "output_file",
    "x_angle": 0.,
    "y_angle": 0.,
    "z_angle": 0.,
    "image_size": [1, 2],
    "model_name": "model_name",
    "part_name": None,
    "color_map": "color_map"
}
image_namespace_full = copy.deepcopy(image_namespace_sparse)
image_namespace_full.update({"part_name": "part_name"}),
image_expected_options_sparse = [
    abaqus_command,
    "--input-file",
    "--output-file",
    "--x-angle",
    "--y-angle",
    "--z-angle",
    "--image-size",
    "--model-name",
    "--color-map"
]
image_unexpected_options_sparse = ["--part-name"]

wrapper_tests = {
    "cylinder": (
        "cylinder",
        cylinder_namespace,
        cylinder_expected_options,
        []
    ),
    "geometry: no output-file": (
        "geometry",
        geometry_namespace_sparse,
        geometry_expected_options_sparse,
        geometry_unexpected_options_sparse
    ),
    "geometry: full": (
        "geometry",
        geometry_namespace_full,
        geometry_expected_options_sparse + geometry_unexpected_options_sparse,
        []
    ),
    "sphere: no input-file": (
        "sphere",
        sphere_namespace_sparse,
        sphere_expected_options_sparse,
        sphere_unexpected_options_sparse
    ),
    "sphere: input-file": (
        "sphere",
        sphere_namespace_full,
        sphere_expected_options_sparse + sphere_unexpected_options_sparse,
        []
    ),
    "partition: no output-file": (
        "partition",
        partition_namespace_sparse,
        partition_expected_options_sparse,
        partition_unexpected_options_sparse
    ),
    "partition: output-file": (
        "partition",
        partition_namespace_full,
        partition_expected_options_sparse + partition_unexpected_options_sparse,
        []
    ),
    "mesh: no output-file": (
        "mesh",
        mesh_namespace_sparse,
        mesh_expected_options_sparse,
        mesh_unexpected_options_sparse
    ),
    "mesh: output-file": (
        "mesh",
        mesh_namespace_full,
        mesh_expected_options_sparse + mesh_unexpected_options_sparse,
        []
    ),
    "export: sparse": (
        "export",
        export_namespace_sparse,
        export_expected_options_sparse,
        export_unexpected_options_sparse
    ),
    "export: full": (
        "export",
        export_namespace_full,
        export_expected_options_sparse + export_unexpected_options_sparse,
        []
    ),
    "image: no part-name": (
        "image",
        image_namespace_sparse,
        image_expected_options_sparse,
        image_unexpected_options_sparse
    ),
    "image: part-name": (
        "image",
        image_namespace_full,
        image_expected_options_sparse + image_unexpected_options_sparse,
        []
    ),
}


@pytest.mark.parametrize("subcommand, namespace, expected_options, unexpected_options",
                         wrapper_tests.values(), ids=wrapper_tests.keys())
def test_image(subcommand, namespace, expected_options, unexpected_options):
    args = argparse.Namespace(**namespace)
    with patch("turbo_turtle._utilities.run_command") as mock_run:
        subcommand_wrapper = getattr(_abaqus_wrappers, subcommand)
        subcommand_wrapper(args, abaqus_command)
    mock_run.assert_called_once()
    command_string = mock_run.call_args[0][0]
    for option in expected_options:
        assert option in command_string
    for option in unexpected_options:
        assert option not in command_string
