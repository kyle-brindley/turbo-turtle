"""
.. warning::

   These are tests of a mixed Python 2/3 compatible module. When updating, be sure to update the Abaqus Python tests to
   match.
"""
import pytest
import numpy
import math

from turbo_turtle._abaqus_python import vertices


compare_xy_values = {
    "horizontal": (
        numpy.array([[0, 0], [1, 0]]), [False, True], None, None
    ),
    "vertical": (
        numpy.array([[0, 0], [0, 1]]), [False, True], None, None
    ),
    "x=y": (
        numpy.array([[0, 0], [1, 1]]), [False, False], None, None
    ),
    "inside default rtol": (
        numpy.array([[100, 0], [100 + 100*5e-6, 1]]), [False, True], None, None
    ),
    "adjust rtol": (
        numpy.array([[100, 0], [100 + 100*5e-6, 1]]), [False, False], 1e-6, None
    ),
}


@pytest.mark.parametrize("coordinates, expected, rtol, atol",
                         compare_xy_values.values(),
                         ids=compare_xy_values.keys())
def test_compare_xy_values(coordinates, expected, rtol, atol):
    bools = vertices._compare_xy_values(coordinates, rtol=rtol, atol=atol)
    assert bools == expected


compare_euclidean_distance = {
    "longer": (
        numpy.array([[0, 0], [1, 0]]), 0.1, [False, True]
    ),
    "shorter": (
        numpy.array([[0, 0], [1, 0]]), 10., [False, False]
    ),
    "equal": (
        numpy.array([[0, 0], [1, 0]]), 1.0, [False, False]
    ),
}


@pytest.mark.parametrize("coordinates, euclidean_distance, expected",
                         compare_euclidean_distance.values(),
                         ids=compare_euclidean_distance.keys())
def test_compare_euclidean_distance(coordinates, euclidean_distance, expected):
    bools = vertices._compare_euclidean_distance(coordinates, euclidean_distance)
    assert bools == expected


bool_via_or = {
    "all true vs all false": (
        [True, True],
        [False, False],
        [True, True]
    ),
    "all false": (
        [False, False],
        [False, False],
        [False, False],
    ),
    "all true": (
        [True, True],
        [True, True],
        [True, True],
    ),
    "true/false mirror": (
        [True, False],
        [False, True],
        [True, True]
    ),
    "true/false mirror 2": (
        [False, True],
        [True, False],
        [True, True]
    ),
}


@pytest.mark.parametrize("bool_list_1, bool_list_2, expected",
                         bool_via_or.values(),
                         ids=bool_via_or.keys())
def test_bool_via_or(bool_list_1, bool_list_2, expected):
    bools = vertices._bool_via_or(bool_list_1, bool_list_2)
    assert bools == expected


break_coordinates = {
    "washer": (
        numpy.array([[1.0, -0.5], [2.0, -0.5], [2.0, 0.5], [1.0, 0.5]]),
        4,
        [numpy.array([[1.0, -0.5]]), numpy.array([[2.0, -0.5]]), numpy.array([[2.0, 0.5]]), numpy.array([[1.0, 0.5]])]
    ),
    "vase": (
        numpy.array([[ 5.1, -5. ],
                     [ 5. , -4.8],
                     [ 4.5, -4. ],
                     [ 4.1, -3. ],
                     [ 4. , -2.5],
                     [ 4. ,  2.5],
                     [ 4.1,  3. ],
                     [ 4.5,  4. ],
                     [ 5. ,  4.8],
                     [ 5.1,  5. ],
                     [ 3. ,  5. ],
                     [ 3. , -4. ],
                     [ 0. , -4. ],
                     [ 0. , -5. ]]),
        4,
        [numpy.array([[ 5.1, -5. ],
                      [ 5. , -4.8],
                      [ 4.5, -4. ],
                      [ 4.1, -3. ],
                      [ 4. , -2.5]]),
         numpy.array([[ 4. ,  2.5],
                      [ 4.1,  3. ],
                      [ 4.5,  4. ],
                      [ 5. ,  4.8],
                      [ 5.1,  5. ]]),
         numpy.array([[ 3.0,  5.0]]),
         numpy.array([[ 3.0, -4.0]]),
         numpy.array([[ 0.0, -4.0]]),
         numpy.array([[ 0.0, -5.0]])]
    )
}


@pytest.mark.parametrize("coordinates, euclidean_distance, expected",
                         break_coordinates.values(),
                         ids=break_coordinates.keys())
def test_break_coordinates(coordinates, euclidean_distance, expected):
    all_splines = vertices._break_coordinates(coordinates, euclidean_distance)
    for spline, expectation in zip(all_splines, expected):
        assert numpy.allclose(spline, expectation)


line_pairs = {
    "washer": (
        [numpy.array([[1.0, -0.5]]), numpy.array([[2.0, -0.5]]), numpy.array([[2.0, 0.5]]), numpy.array([[1.0, 0.5]])],
        [(numpy.array([1.0, -0.5]), numpy.array([2.0, -0.5])),
         (numpy.array([2.0, -0.5]), numpy.array([2.0,  0.5])),
         (numpy.array([2.0,  0.5]), numpy.array([1.0,  0.5])),
         (numpy.array([1.0,  0.5]), numpy.array([1.0, -0.5]))]
    ),
    "vase": (
        [numpy.array([[ 5.1, -5. ],
                      [ 5. , -4.8],
                      [ 4.5, -4. ],
                      [ 4.1, -3. ],
                      [ 4. , -2.5]]),
         numpy.array([[ 4. ,  2.5],
                      [ 4.1,  3. ],
                      [ 4.5,  4. ],
                      [ 5. ,  4.8],
                      [ 5.1,  5. ]]),
         numpy.array([[ 3.0,  5.0]]),
         numpy.array([[ 3.0, -4.0]]),
         numpy.array([[ 0.0, -4.0]]),
         numpy.array([[ 0.0, -5.0]])],
        [(numpy.array([ 4. , -2.5]), numpy.array([ 4. ,  2.5])),
         (numpy.array([ 5.1,  5. ]), numpy.array([ 3.0,  5.0])),
         (numpy.array([ 3.0,  5.0]), numpy.array([ 3.0, -4.0])),
         (numpy.array([ 3.0, -4.0]), numpy.array([ 0.0, -4.0])),
         (numpy.array([ 0.0, -4.0]), numpy.array([ 0.0, -5.0])),
         (numpy.array([ 0.0, -5.0]), numpy.array([ 5.1, -5. ]))]
    ),
}


@pytest.mark.parametrize("all_splines, expected",
                         line_pairs.values(),
                         ids=line_pairs.keys())
def test_line_pairs(all_splines, expected):
    line_pairs = vertices._line_pairs(all_splines)
    for pair, expectation in zip(line_pairs, expected):
        assert len(pair) == len(expectation)
        assert numpy.allclose(pair[0], expectation[0])
        assert numpy.allclose(pair[1], expectation[1])


the_real_mccoy = {
    "washer": (
        numpy.array([[1.0, -0.5], [2.0, -0.5], [2.0, 0.5], [1.0, 0.5]]),
        4,
        [(numpy.array([1.0, -0.5]), numpy.array([2.0, -0.5])),
         (numpy.array([2.0, -0.5]), numpy.array([2.0,  0.5])),
         (numpy.array([2.0,  0.5]), numpy.array([1.0,  0.5])),
         (numpy.array([1.0,  0.5]), numpy.array([1.0, -0.5]))],
        []
    ),
    "vase": (
        numpy.array([[ 5.1, -5. ],
                     [ 5. , -4.8],
                     [ 4.5, -4. ],
                     [ 4.1, -3. ],
                     [ 4. , -2.5],
                     [ 4. ,  2.5],
                     [ 4.1,  3. ],
                     [ 4.5,  4. ],
                     [ 5. ,  4.8],
                     [ 5.1,  5. ],
                     [ 3. ,  5. ],
                     [ 3. , -4. ],
                     [ 0. , -4. ],
                     [ 0. , -5. ]]),
        4,
        [(numpy.array([ 4. , -2.5]), numpy.array([ 4. ,  2.5])),
         (numpy.array([ 5.1,  5. ]), numpy.array([ 3.0,  5.0])),
         (numpy.array([ 3.0,  5.0]), numpy.array([ 3.0, -4.0])),
         (numpy.array([ 3.0, -4.0]), numpy.array([ 0.0, -4.0])),
         (numpy.array([ 0.0, -4.0]), numpy.array([ 0.0, -5.0])),
         (numpy.array([ 0.0, -5.0]), numpy.array([ 5.1, -5. ]))],
        [numpy.array([[ 5.1, -5. ],
                      [ 5. , -4.8],
                      [ 4.5, -4. ],
                      [ 4.1, -3. ],
                      [ 4. , -2.5]]),
         numpy.array([[ 4. ,  2.5],
                      [ 4.1,  3. ],
                      [ 4.5,  4. ],
                      [ 5. ,  4.8],
                      [ 5.1,  5. ]])]
    )
}


@pytest.mark.parametrize("coordinates, euclidean_distance, expected_lines, expected_splines",
                         the_real_mccoy.values(),
                         ids=the_real_mccoy.keys())
def test_lines_and_splines(coordinates, euclidean_distance, expected_lines, expected_splines):
    """Test :meth:`turbo_turtle._abaqus_python.vertices.lines_and_splines`"""
    lines, splines = vertices.lines_and_splines(coordinates, euclidean_distance)
    for pair, expectation in zip(lines, expected_lines):
        assert len(pair) == len(expectation)
        assert numpy.allclose(pair[0], expectation[0])
        assert numpy.allclose(pair[1], expectation[1])
    assert len(splines) == len(expected_splines)
    for spline, expectation in zip(splines, expected_splines):
        assert numpy.allclose(spline, expectation)


def test_cylinder():
    """Test :meth:`turbo_turtle._abaqus_python.vertices.cylinder`"""
    expected = numpy.array([[1., 1.], [2., 1.], [2., 0.], [1., 0.]])
    coordinates = vertices.cylinder(1., 2., 1.)
    assert numpy.allclose(coordinates, expected)


number = math.sqrt(2.**2 / 2.)
rectalinear_coordinates = {
    "unit circle": (
        (1, 1, 1, 1), (0, math.pi / 2, math.pi, 2 * math.pi), ((1, 0), (0, 1), (-1, 0), (1, 0))
    ),
    "forty-fives": (
        (2, 2, 2, 2), (math.pi / 4, math.pi * 3 / 4, math.pi * 5 / 4, math.pi * 7 / 4),
        ((number, number), (-number, number), (-number, -number), (number, -number))
    )
}


@pytest.mark.parametrize("radius_list, angle_list, expected",
                         rectalinear_coordinates.values(),
                         ids=rectalinear_coordinates.keys())
def test_rectalinear_coordinates(radius_list, angle_list, expected):
    """Test :meth:`turbo_turtle._abaqus_python.vertices.rectalinear_coordinates`"""
    coordinates = vertices.rectalinear_coordinates(radius_list, angle_list)
    assert numpy.allclose(coordinates, expected)


one_over_root_three = 1. / math.sqrt(3.)
normalize_vector = {
    "zero": (
        (0., 0., 0.), numpy.array([0., 0., 0.])
    ),
    "unit x-axis": (
        (1., 0., 0.), numpy.array([1., 0., 0.])
    ),
    "unit y-axis": (
        (0., 1., 0.), numpy.array([0., 1., 0.])
    ),
    "unit z-axis": (
        (0., 0., 1.), numpy.array([0., 0., 1.])
    ),
    "unit equal": (
        (1., 1., 1.), numpy.array([one_over_root_three, one_over_root_three, one_over_root_three])
    ),
    "twice unit equal": (
        (2., 2., 2.), numpy.array([one_over_root_three, one_over_root_three, one_over_root_three])
    ),
}


@pytest.mark.parametrize("vector, expected",
                         normalize_vector.values(),
                         ids=normalize_vector.keys())
def test_normalize_vector(vector, expected):
    normalized = vertices.normalize_vector(vector)
    assert numpy.allclose(normalized, expected)


def test_midpoint_vector():
    first = [1., 0, 0]
    second = [0, 1., 0]
    expected = numpy.array([0.5, 0.5, 0.])
    midpoint = vertices.midpoint_vector(first, second)
    assert numpy.allclose(midpoint, expected)


norm = math.sqrt(0.5)
datum_planes = {
    "globally aligned 45-degrees": (
        (1., 0., 0.), (0., 0., 1.),
        [
         numpy.array([0., 0., 1.]),  # XY plane
         numpy.array([1., 0., 0.]),  # YZ plane
         numpy.array([0., 1., 0.]),  # ZX plane
         numpy.array([ norm,  norm, 0.]),
         numpy.array([ norm, -norm, 0.]),
         numpy.array([ 0., norm,  norm]),
         numpy.array([ 0., norm, -norm]),
         numpy.array([  norm, 0., norm]),
         numpy.array([ -norm, 0., norm])
        ]
    ),
}


@pytest.mark.parametrize("xvector, zvector, expected",
                         datum_planes.values(),
                         ids=datum_planes.keys())
def test_datum_planes(xvector, zvector, expected):
    planes = vertices.datum_planes(xvector, zvector)
    for plane, expectation in zip(planes, expected):
        assert numpy.allclose(plane, expectation)
