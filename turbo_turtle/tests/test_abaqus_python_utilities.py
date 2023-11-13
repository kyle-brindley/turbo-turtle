from unittest.mock import patch
from contextlib import nullcontext as does_not_raise

import numpy
import pytest

from turbo_turtle._abaqus_python import _utilities


validate_part_name = {
    "None one": (
        ["dummy.ext"], [None], ["dummy"], does_not_raise()
    ),
    "None two": (
        ["thing1.ext", "thing2.ext"], [None], ["thing1", "thing2"], does_not_raise()
    ),
    "one part": (
        ["one_part.ext"], ["part_one"], ["part_one"], does_not_raise()
    ),
    "two part": (
        ["one_part.ext", "two_part.ext"], ["part_one", "part_two"], ["part_one", "part_two"], does_not_raise()
    ),
    "seuss": (
        ["one_part.ext", "two_part.ext", "red_part.ext", "blue_part.ext"],
        ["part_one", "part_two", "part_red", "part_blue"],
        ["part_one", "part_two", "part_red", "part_blue"],
        does_not_raise()
    ),
    "wrong length: 2-1": (
        ["one_part.ext", "two_part.ext"],
        ["part_one"],
        [],
        pytest.raises(RuntimeError)
    ),
    "wrong length: 1-2": (
        ["one_part.ext"],
        ["part_one", "part_two"],
        [],
        pytest.raises(RuntimeError)
    ),
}


@pytest.mark.parametrize("input_file, original_part_name, expected, outcome",
                         validate_part_name.values(),
                         ids=validate_part_name.keys())
def test_validate_part_name(input_file, original_part_name, expected, outcome):
    with outcome:
        try:
            part_name = _utilities.validate_part_name(input_file, original_part_name)
            assert part_name == expected
        finally:
            pass


return_genfromtxt = {
    "good shape": (
        "dummy", ",", 0, None, None, numpy.array([[0, 0], [1, 1]]), does_not_raise()
    ),
    "unexpected column": (
        "dummy", ",", 0, None, 3, numpy.array([[0, 0], [1, 1]]), pytest.raises(RuntimeError)
    ),
    "unexpected dimensions": (
        "dummy", ",", 0, 1, None, numpy.array([[0, 0], [1, 1]]), pytest.raises(RuntimeError)
    ),
}


validate_element_type = {
    "default": (
        1, [None], [None], does_not_raise()
    ),
    "two parts": (
        2, [None], [None, None], does_not_raise()
    ),
    "two element types": (
        2, ["C3D8"], ["C3D8", "C3D8"], does_not_raise()
    ),
    "one parts, two element types": (
        1, ["C3D8", "C3D8"], [], pytest.raises(RuntimeError)
    ),
    "three parts, two element types": (
        3, ["C3D8", "C3D8"], [], pytest.raises(RuntimeError)
    ),
}


@pytest.mark.parametrize("length_part_name, original_element_type, expected, outcome",
                         validate_element_type.values(),
                         ids=validate_element_type.keys())
def test_validate_element_type(length_part_name, original_element_type, expected, outcome):
    with outcome:
        try:
            element_type = _utilities.validate_element_type(length_part_name, original_element_type)
            assert element_type == expected
        finally:
            pass


@pytest.mark.parametrize("length_part_name, original_element_type, expected, outcome",
                         validate_element_type.values(),
                         ids=validate_element_type.keys())
def test_validate_element_type_or_exit(length_part_name, original_element_type, expected, outcome):
    if outcome == pytest.raises(RuntimeError):
        outcome = pytest.raises(SystemExit)
    with outcome:
        try:
            element_type = _utilities.validate_element_type(length_part_name, original_element_type)
            assert element_type == expected
        finally:
            pass


@pytest.mark.parametrize("file_name, delimiter, header_lines, expected_dimensions, expected_columns, expected, outcome",
                         return_genfromtxt.values(),
                         ids=return_genfromtxt.keys())
def test_return_genfromtxt(file_name, delimiter, header_lines, expected_dimensions, expected_columns, expected, outcome):
    with patch("builtins.open"), patch("numpy.genfromtxt", return_value=expected) as mock_genfromtxt, outcome:
        try:
            coordinates = _utilities.return_genfromtxt(file_name, delimiter=delimiter, header_lines=header_lines,
                                                       expected_dimensions=expected_dimensions,
                                                       expected_columns=expected_columns)
            assert numpy.allclose(coordinates, expected)
        finally:
            pass


def test_sys_exit():
    with patch("sys.exit") as mock_exit:
        _utilities.sys_exit("message")
        mock_exit.assert_called_once_with("message")
