import unittest

from hypothesis import given, strategies as st
import hypothesis.extra.numpy as hnp
import numpy as np
import numpy.testing as npt

from src.segregation_indices import calc_indices
from src.exceptions import SpatSegValueError


class TestCalcIndices(unittest.TestCase):

    @given(
        arr=hnp.arrays(np.float, shape=(6, 80))
    )
    def test_value_error(self, arr):
        with self.assertRaises(SpatSegValueError):
            calc_indices(arr)


if __name__ == '__main__':
    unittest.main()
