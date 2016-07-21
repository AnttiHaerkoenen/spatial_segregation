import unittest

import numpy as np
import pandas as pd
import pandas.util.testing as pdt

from spatial_segregation import kde

data1 = pd.DataFrame(np.random.randint(0, 1000, (20, 4)), columns='x y host other'.split())
data2 = pd.DataFrame(np.ones((2, 4)), columns='x y host other'.split())
data3 = {'x': np.array((0, 1, 1)),
         'y': np.array((0, 1, 1))}


class TestKDE(unittest.TestCase):
    def test_create_kde(self):
        kde1 = kde.create_kde_surface(data2, 20, 'distance_decay', 25, 1)
        kde2 = pd.DataFrame({
            'host': [0.0, 0.0, 0.0, 0.0, 1.7037037037, 0.857142857143, 0.0, 0.857142857143, 0.325581395349],
            'other': [0.0, 0.0, 0.0, 0.0, 1.7037037037, 0.857142857143, 0.0, 0.857142857143, 0.325581395349],
            'x': [-24.0, -4.0, 16.0, -24.0, -4.0, 16.0, -24.0, -4.0, 16.0],
            'y': [-24.0, -24.0, -24.0, -4.0, -4.0, -4.0, 16.0, 16.0, 16.0]
        })
        pdt.assert_frame_equal(kde1, kde2)


class TestD(unittest.TestCase):
    def test_calc_d(self):
        self.assertAlmostEqual(kde.calc_d(data2, data3).all(),
                               np.array([[1, 0, 0], [1, 0, 0]]).all())


class TestW(unittest.TestCase):
    def test_calc_w(self):
        d = np.array([[0, 2, 4], [0, 2, 4]])
        w = kde.calc_w(d, 'distance_decay', bw=4, a=1)
        self.assertAlmostEqual(w.all(), np.array([[1, 0.6, 0], [1, 0.6, 0]]).all())


if __name__ == '__main__':
    unittest.main()
