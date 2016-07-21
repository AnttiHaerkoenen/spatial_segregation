import unittest

import pandas as pd
import pandas.util.testing as pdt
import numpy as np

from spatial_segregation import data

df = pd.DataFrame(np.random.rand(18, 2), columns=list('xy'))
df = df.append(pd.DataFrame([[0, 0], [1, 1]], columns=list('xy')), ignore_index=True)

pop_data = None
loc_data = None


class TestData(unittest.TestCase):
    def test_add_coordinates(self):
        df1 = pd.DataFrame()
        df2 = pd.DataFrame()
        pdt.assert_frame_equal(df1, df2)

    def test_get_x_lim(self):
        self.assertEqual(data.get_x_limits(df), (1, 0))

    def test_get_y_lim(self):
        self.assertEqual(data.get_y_limits(df), (1, 0))


if __name__ == '__main__':
    unittest.main()
