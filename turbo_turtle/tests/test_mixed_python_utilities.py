"""
.. warning::

   These are tests of a mixed Python 2/3 compatible module. When updating, be sure to update the Abaqus Python tests to
   match.
"""

from unittest.mock import patch
from contextlib import nullcontext as does_not_raise

import numpy
import pytest

from turbo_turtle._abaqus_python import _utilities


def test_sys_exit():
    """Test :meth:`turbo_turtle._abaqus_python._utilities.sys_exit` sys.exit wrapper.

    We can't test the Abaqus Python override print to ``sys.__stderr__`` because the print statement is not valid Python
    3 code.
    """
    with patch("sys.exit") as mock_exit:
        _utilities.sys_exit("message")
        mock_exit.assert_called_once_with("message")


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
    """Test :meth:`turbo_turtle._abaqus_python._utilities.validate_part_name`

    Tests both the expection raising version and the system exit version
    :meth:`turbo_turtle._abaqus_python._utilities.validate_part_name_or_exit`

    :param str input_file: dummy input file name
    :param list original_part_name: List of part names passed to function under test
    :param list expected: Expected list of part names returned by function under test
    :param outcome: either contextlib.nullcontext or pytest.raises() depending on expected success or exception,
        respectively
    """
    with outcome:
        try:
            part_name = _utilities.validate_part_name(input_file, original_part_name)
            assert part_name == expected
        finally:
            pass

    # TODO: Figure out how to check against pytest.raises() instead.
    if not isinstance(outcome, does_not_raise):
        outcome = pytest.raises(SystemExit)
    with outcome:
        try:
            part_name = _utilities.validate_part_name_or_exit(input_file, original_part_name)
            assert part_name == expected
        finally:
            pass


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
    """Test :meth:`turbo_turtle._abaqus_python._utilities.validate_element_type`

    Tests both the expection raising version and the system exit version
    :meth:`turbo_turtle._abaqus_python._utilities.validate_element_type_or_exit`

    :param int length_part_name: length of the ``part_name`` list
    :param list original_element_type: List of element types passed to function under test
    :param list expected: Expected list of element types returned by function under test
    :param outcome: either contextlib.nullcontext or pytest.raises() depending on expected success or exception,
        respectively
    """
    with outcome:
        try:
            element_type = _utilities.validate_element_type(length_part_name, original_element_type)
            assert element_type == expected
        finally:
            pass

    # TODO: Figure out how to check against pytest.raises() instead.
    if not isinstance(outcome, does_not_raise):
        outcome = pytest.raises(SystemExit)
    with outcome:
        try:
            element_type = _utilities.validate_element_type_or_exit(length_part_name, original_element_type)
            assert element_type == expected
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


@pytest.mark.parametrize("file_name, delimiter, header_lines, expected_dimensions, expected_columns, expected, outcome",
                         return_genfromtxt.values(),
                         ids=return_genfromtxt.keys())
def test_return_genfromtxt(file_name, delimiter, header_lines, expected_dimensions, expected_columns, expected, outcome):
    """Test :meth:`turbo_turtle._abaqus_python._utilities.return_genfromtxt`

    Tests both the expection raising version and the system exit version
    :meth:`turbo_turtle._abaqus_python._utilities.return_genfromtxt_or_exit`

    :param str file_name: dummy data file name
    :param str delimiter: String for file name delimiter character
    :param int header_lines: Integer number of header lines to ignore
    :param int expected_dimensions: The expected dimensionality of the data. When mismatched, should trigger an
        exception/error.
    :param int expected_columns: The expected number of columns of the data. When mismatched, should trigger an
        exception/error.
    :param numpy.array expected: expected return data of the function under test
    :param outcome: either contextlib.nullcontext or pytest.raises() depending on expected success or exception,
        respectively
    """
    with patch("builtins.open"), patch("numpy.genfromtxt", return_value=expected) as mock_genfromtxt, outcome:
        try:
            coordinates = _utilities.return_genfromtxt(file_name, delimiter=delimiter, header_lines=header_lines,
                                                       expected_dimensions=expected_dimensions,
                                                       expected_columns=expected_columns)
            assert numpy.allclose(coordinates, expected)
        finally:
            pass

    # TODO: Figure out how to check against pytest.raises() instead.
    if not isinstance(outcome, does_not_raise):
        outcome = pytest.raises(SystemExit)
    with patch("builtins.open"), patch("numpy.genfromtxt", return_value=expected) as mock_genfromtxt, outcome:
        try:
            coordinates = _utilities.return_genfromtxt_or_exit(file_name, delimiter=delimiter, header_lines=header_lines,
                                                               expected_dimensions=expected_dimensions,
                                                               expected_columns=expected_columns)
            assert numpy.allclose(coordinates, expected)
        finally:
            pass


remove_duplicate_items = {
    "no duplicates": (
        ["thing1", "thing2"], ["thing1", "thing2"]
    ),
    "one duplicate": (
        ["thing1", "thing2", "thing1"], ["thing1", "thing2"]
    ),
}


@pytest.mark.parametrize("string_list, expected",
                         remove_duplicate_items.values(),
                         ids=remove_duplicate_items.keys())
def test_remove_duplicate_items(string_list, expected):
    with patch("sys.stderr.write") as mock_stderr_write:
        unique = _utilities.remove_duplicate_items(string_list)
        assert unique == expected
        if unique != string_list:
            mock_stderr_write.assert_called_once()
        else:
            mock_stderr_write.assert_not_called()


intersection_of_lists = {
    "None requested": (
        [None], ["thing1", "thing2"], ["thing1", "thing2"]
    ),
    "exact": (
        ["thing1", "thing2"], ["thing1", "thing2"], ["thing1", "thing2"]
    ),
    "one": (
        ["thing1"], ["thing1", "thing2"], ["thing1"]
    ),
}


@pytest.mark.parametrize("requested, available, expected",
                         intersection_of_lists.values(),
                         ids=intersection_of_lists.keys())
def test_intersection_of_lists(requested, available, expected):
        intersection = _utilities.intersection_of_lists(requested, available)
        assert intersection == expected
