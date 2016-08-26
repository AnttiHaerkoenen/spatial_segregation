import unittest

import pandas as pd
import pandas.util.testing as pdt
import numpy as np

from spatial_segregation import data

df = pd.DataFrame(np.random.rand(18, 2), columns=list('xy'))
df = df.append(pd.DataFrame([[0, 0], [1, 1]], columns=list('xy')), ignore_index=True)

pop_data = [[1, 2, 0], [2, 9, 0], [2, 5, 0],
            [2, 8, 0], [2, 1, 0], [3, 0, 0],
            [4, 2, 0], [5, 1, 0], [5, 1, 0],
            [5, 3, 0], [5, 2, 0]]

pop_data_aggregate = [[1, 2, 0],
                      [2, 23, 0],
                      [3, 0, 0],
                      [4, 2, 0],
                      [5, 7, 0]]

loc_data = [[1, 594441.4386, 6732193.0218],
            [2, 594451.5888999999, 6732221.8068],
            [3, 594467.5268000001, 6732243.441299999],
            [4, 594481.0416000001, 6732257.1997],
            [5, 594514.3106000004, 6732244.615]]

combined_data = pd.DataFrame(
    {
        'x': [594441.4386, 594451.5889, 594467.5268, 594481.0416, 594514.3106],
        'y': [6732193.0218, 6732221.8068, 6732243.4413, 6732257.1997, 6732244.6150],
        'host': [2, 23, 0, 2, 7],
        'other': [0, 0, 0, 0, 0]
    }, index=range(1, 6), columns="x y host other".split())


class TestAddCoordinates(unittest.TestCase):
    def test_add_coordinates(self):
        df1 = data.add_coordinates(pop_data_aggregate, loc_data)
        df2 = combined_data
        pdt.assert_frame_equal(df1, df2)


class TestAggregateSum(unittest.TestCase):
    def test_aggregate_sum(self):
        # TODO
        pass


class TestShuffle(unittest.TestCase):
    def test_shuffle(self):
        # TODO
        pass


class TestRange(unittest.TestCase):
    def test_get_x_lim(self):
        self.assertEqual(data.get_x_limits(df), (1, 0))

    def test_get_y_lim(self):
        self.assertEqual(data.get_y_limits(df), (1, 0))


if __name__ == '__main__':
    unittest.main()
