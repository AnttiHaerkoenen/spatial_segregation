import unittest

from hypothesis import given
import hypothesis.strategies as st
import hypothesis.extra.numpy as hynp

from src.kernel_functions import *


class TestEpanechnikov(unittest.TestCase):

    @given(
        a=hynp.arrays(
            np.float,
            shape=(11,11),
            elements=st.floats(0)
        ),
        bw=st.floats(0)
    )
    def test_min(self, a, bw):
        smaller = epanechnikov(a, bw) >= 0
        self.assertEqual(smaller.all(), True)


if __name__ == '__main__':
    unittest.main()
