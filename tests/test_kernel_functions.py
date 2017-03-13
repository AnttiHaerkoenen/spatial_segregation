import unittest

from hypothesis import given, settings, Verbosity, strategies as st
import hypothesis.extra.numpy as hnp
import numpy as np
import numpy.testing as npt

from src.kernel_functions import epanechnikov, uniform, gaussian, triangle, biweight
from src.exceptions import SSTypeError, SSValueError


class TestEpanechnikov(unittest.TestCase):
    @given(
        arr=hnp.arrays(np.float, shape=(6, 6, 6), elements=st.floats(0, 100)),
        bw=st.floats(0.0001, 100)
    )
    @settings(verbosity=Verbosity.verbose)
    def test_min(self, arr, bw):
        is_positive = epanechnikov(arr, bw) >= 0
        self.assertEqual(is_positive.all(), True)

    @given(
        arr=hnp.arrays(np.float, shape=(6, 6, 6), elements=st.floats(0, 100)),
        bw=st.floats(0.0001, 100)
    )
    def test_max(self, arr, bw):
        less_than_1 = epanechnikov(arr, bw) <= 1
        self.assertEqual(less_than_1.all(), True)

    @given(
        arr=hnp.arrays(np.float, shape=(11, 2), elements=st.floats(0)),
        bw=st.floats(-1000, 0)
    )
    def test_value_error(self, arr, bw):
        with self.assertRaises(SSValueError):
            epanechnikov(arr, bw)

    @given(
        arr=st.one_of(
            st.none(),
            st.lists(st.floats()),
            st.tuples(st.booleans()),
            st.dictionaries(keys=st.integers(), values=st.floats()),
            st.text()
        ),
        bw=st.floats(0.0001, 100)
    )
    def test_type_error(self, arr, bw):
        with self.assertRaises(SSTypeError):
            epanechnikov(arr, bw)

    @given(
        arr=hnp.arrays(np.float, shape=0, elements=st.floats(0)),
        bw=st.floats(0.0001, 100)
    )
    def test_empty(self, arr, bw):
        npt.assert_array_equal(np.empty_like(arr), epanechnikov(arr, bw))


class TestTriangle(unittest.TestCase):
    @given(
        arr=hnp.arrays(np.float, shape=(6, 6, 6), elements=st.floats(0, 100)),
        bw=st.floats(0.0001, 100)
    )
    def test_min(self, arr, bw):
        is_positive = triangle(arr, bw) >= 0
        self.assertEqual(is_positive.all(), True)

    @given(
        arr=hnp.arrays(np.float, shape=(6, 6, 6), elements=st.floats(0, 100)),
        bw=st.floats(0.0001, 100)
    )
    def test_max(self, arr, bw):
        less_than_1 = triangle(arr, bw) <= 1
        self.assertEqual(less_than_1.all(), True)

    @given(
        arr=hnp.arrays(np.float, shape=(11, 2), elements=st.floats(0)),
        bw=st.floats(-1000, 0)
    )
    def test_value_error(self, arr, bw):
        with self.assertRaises(SSValueError):
            triangle(arr, bw)

    @given(
        arr=st.one_of(
            st.none(),
            st.lists(st.floats()),
            st.tuples(st.booleans()),
            st.dictionaries(keys=st.integers(), values=st.floats()),
            st.text()
        ),
        bw=st.floats(0.0001, 100)
    )
    def test_type_error(self, arr, bw):
        with self.assertRaises(SSTypeError):
            triangle(arr, bw)

    @given(
        arr=hnp.arrays(np.float, shape=0, elements=st.floats(0)),
        bw=st.floats(0.0001, 100)
    )
    def test_empty(self, arr, bw):
        npt.assert_array_equal(np.empty_like(arr), triangle(arr, bw))


class TestGaussian(unittest.TestCase):
    @given(
        arr=hnp.arrays(np.float, shape=(6, 6, 6), elements=st.floats(0, 100)),
        sigma=st.floats(0.0001, 100)
    )
    def test_min(self, arr, sigma):
        is_positive = gaussian(arr, sigma) >= 0
        self.assertEqual(is_positive.all(), True)

    @given(
        arr=hnp.arrays(np.float, shape=(11, 2), elements=st.floats(0)),
        sigma=st.floats(-1000, 0)
    )
    def test_value_error(self, arr, sigma):
        with self.assertRaises(SSValueError):
            gaussian(arr, sigma)

    @given(
        arr=st.one_of(
            st.none(),
            st.lists(st.floats()),
            st.tuples(st.booleans()),
            st.dictionaries(keys=st.integers(), values=st.floats()),
            st.text()
        ),
        sigma=st.floats(0.0001, 100)
    )
    def test_type_error(self, arr, sigma):
        with self.assertRaises(SSTypeError):
            gaussian(arr, sigma)

    @given(
        arr=hnp.arrays(np.float, shape=0, elements=st.floats(0)),
        sigma=st.floats(0.0001, 100)
    )
    def test_empty(self, arr, sigma):
        npt.assert_array_equal(np.empty_like(arr), gaussian(arr, sigma))


class TestBiweight(unittest.TestCase):
    @given(
        arr=hnp.arrays(np.float, shape=(6, 6, 6), elements=st.floats(0, 100)),
        bw=st.floats(0.0001, 100),
        a=st.floats(0.01, 5)
    )
    def test_min(self, arr, bw, a):
        is_positive = biweight(arr, bw, a) >= 0
        self.assertEqual(is_positive.all(), True)

    @given(
        arr=hnp.arrays(np.float, shape=(6, 6, 6), elements=st.floats(0, 100)),
        bw=st.floats(0.0001, 100),
        a=st.floats(0.01, 5)
    )
    def test_max(self, arr, bw, a):
        less_than_1 = biweight(arr, bw, a) <= 1
        self.assertEqual(less_than_1.all(), True)

    @given(
        arr=hnp.arrays(np.float, shape=(11, 2), elements=st.floats(0)),
        bw=st.floats(-1000, 0),
        a=st.floats(0.01, 5)
    )
    def test_value_error_1(self, arr, bw, a):
        with self.assertRaises(SSValueError):
            biweight(arr, bw, a)

    @given(
        arr=hnp.arrays(np.float, shape=(11, 2), elements=st.floats(0)),
        bw=st.floats(0.0001, 100),
        a=st.floats(-100, 0)
    )
    def test_value_error_2(self, arr, bw, a):
        with self.assertRaises(SSValueError):
            biweight(arr, bw, a)

    @given(
        arr=st.one_of(
            st.none(),
            st.lists(st.floats()),
            st.tuples(st.booleans()),
            st.dictionaries(keys=st.integers(), values=st.floats()),
            st.text()
        ),
        bw=st.floats(0.0001, 100)
    )
    def test_type_error(self, arr, bw):
        with self.assertRaises(SSTypeError):
            biweight(arr, bw)

    @given(
        arr=hnp.arrays(np.float, shape=0, elements=st.floats(0)),
        bw=st.floats(0.0001, 100)
    )
    def test_empty(self, arr, bw):
        npt.assert_array_equal(np.empty_like(arr), biweight(arr, bw))


class TestUniform(unittest.TestCase):
    @given(
        arr=hnp.arrays(np.float, shape=(6, 6, 6), elements=st.floats(0, 100)),
        bw=st.floats(0.0001, 100)
    )
    def test_min(self, arr, bw):
        is_positive = uniform(arr, bw) >= 0
        self.assertEqual(is_positive.all(), True)

    @given(
        arr=hnp.arrays(np.float, shape=(11, 2), elements=st.floats(0)),
        bw=st.floats(-1000, 0)
    )
    def test_value_error(self, arr, bw):
        with self.assertRaises(SSValueError):
            uniform(arr, bw)

    @given(
        arr=st.one_of(
            st.none(),
            st.lists(st.floats()),
            st.tuples(st.booleans()),
            st.dictionaries(keys=st.integers(), values=st.floats()),
            st.text()
        ),
        bw=st.floats(0.0001, 100)
    )
    def test_type_error(self, arr, bw):
        with self.assertRaises(SSTypeError):
            uniform(arr, bw)

    @given(
        arr=hnp.arrays(np.float, shape=0, elements=st.floats(0)),
        bw=st.floats(0.0001, 100)
    )
    def test_empty(self, arr, bw):
        npt.assert_array_equal(np.empty_like(arr), uniform(arr, bw))


if __name__ == '__main__':
    unittest.main()
