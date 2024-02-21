"""
.. warning::

   These tests are duplicates of the Python 3 tests in :meth:`turbo_turtle.tests.test_parsers`
"""
import os
import sys
import inspect
import unittest

import numpy

filename = inspect.getfile(lambda: None)
basename = os.path.basename(filename)
parent = os.path.dirname(filename)
sys.path.insert(0, parent)
import parsers


class TestParsers(unittest.TestCase):
    """Abaqus Python unittests for :meth:`turbo_turtle._abaqus_python.parsers`"""

    def test_positive_float(self):
        tests = [
            ("0.", 0.),
            ("1.", 1.)
        ]
        for input_string, expected_float in tests:
            argument = parsers.positive_float(input_string)
            assert numpy.isclose(argument, expected_float)

    @unittest.expectedFailure
    def test_positive_float_negative_exception():
        argument = parsers.positive_float("-1.")

    @unittest.expectedFailure
    def test_positive_float_nonfloat_exception():
        argument = parsers.positive_float("negative_one")

    def test_positive_int(self):
        tests = [
            ("0", 0),
            ("1", 1)
        ]
        for input_string, expected_int in tests:
            argument = parsers.positive_int(input_string)
            assert numpy.isclose(argument, expected_int)

    @unittest.expectedFailure
    def test_positive_int_negative_exception():
        argument = parsers.positive_int("-1.")

    @unittest.expectedFailure
    def test_positive_int_nonint_exception():
        argument = parsers.positive_int("negative_one")
