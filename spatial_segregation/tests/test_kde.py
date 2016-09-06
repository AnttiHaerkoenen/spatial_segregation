import unittest

import numpy as np
import numpy.testing as npt
import pandas as pd
import pandas.util.testing as pdt

from spatial_segregation import kde

data1 = pd.DataFrame(np.random.randint(0, 1000, (20, 4)), columns='x y host other'.split())

data2 = pd.DataFrame({'x': [-100, 100, 100, -100],
                      'y': [100, 100, -100, -100],
                      'host': [2, 2, 2, 2],
                      'other': [0, 0, 0, 1]})

data3 = {'x': np.array((0, 1, 1)),
         'y': np.array((0, 1, 1))}

data4 = {'x': np.array((-1, 1, 1, -1)),
         'y': np.array((1, 1, -1, -1))}

data5 = {'x': np.array((-2, 2, 2, -2)),
         'y': np.array((1, 1, -1, -1))}

data6 = {'x': np.array((-0.5, 0.5, 0.5, -0.5)),
         'y': np.array((0.5, 0.5, -0.5, -0.5))}

data_ones = pd.DataFrame(np.ones((2, 4)), columns='x y host other'.split())

data_empty = {'x': np.array(()),
              'y': np.array(())}


class TestKDE(unittest.TestCase):
    def test_create_kde(self):
        kde1 = kde.create_kde_surface(data2, 100, 'distance_decay', 500, 1)
        kde2 = pd.DataFrame({
            'host': [5.9268547544409609, 6.3589743589743595, 5.9268547544409609, 6.3589743589743595, 6.8148148148148149,
                     6.3589743589743586, 5.9268547544409609, 6.3589743589743586, 5.9268547544409609],
            'other': [1.0, 0.92307692307692313, 0.72413793103448276, 0.92307692307692313, 0.85185185185185186,
                      0.66666666666666663, 0.72413793103448276, 0.66666666666666663, 0.51515151515151514],
            'x': [-100, 0, 100, -100, 0, 100, -100, 0, 100],
            'y': [-100, -100, -100, 0, 0, 0, 100, 100, 100]
        })
        pdt.assert_frame_equal(kde1, kde2)


class TestD(unittest.TestCase):
    def test_calc_d(self):
        self.assertAlmostEqual(kde.calc_d(data_ones, data3).all(),
                               np.array([[1, 0, 0], [1, 0, 0]]).all())


class TestW(unittest.TestCase):
    def test_calc_w(self):
        d = np.array([[0, 2, 4], [0, 2, 4]])
        w = kde.calc_w(d, 'distance_decay', bw=4, a=1)
        self.assertAlmostEqual(w.all(), np.array([[1, 0.6, 0], [1, 0.6, 0]]).all())


class TestSelectByLocation(unittest.TestCase):
    def test_same_points(self):
        mcp = kde.get_convex_hull(data4)
        selection = kde.select_by_location(data4, mcp)

        for k in list('xy'):
            npt.assert_array_equal(selection[k], data4[k])

    def test_all_out(self):
        mcp = kde.get_convex_hull(data4)
        selection = kde.select_by_location(data5, mcp)

        for k in list('xy'):
            npt.assert_array_equal(selection[k], data_empty[k])

    def test_all_in(self):
        mcp = kde.get_convex_hull(data4)
        selection = kde.select_by_location(data6, mcp)

        for k in list('xy'):
            npt.assert_array_equal(selection[k], data6[k])


class TestConvexHull(unittest.TestCase):
    def test_convex_creation(self):
        pass

    def test_one_point(self):
        pass

    def test_zero_points(self):
        pass

    def test_same_points(self):
        pass


if __name__ == '__main__':
    unittest.main()
