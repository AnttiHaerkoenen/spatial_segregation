import unittest

import numpy as np

import spatial_segregation.segregation_indices as si

rand = np.random.rand(1, 50)
zeros = np.zeros((1, 50))
data_a = np.tile(rand, (2, 2)).T
data_b = np.hstack((np.vstack((rand, zeros)), np.vstack((zeros, rand)))).T

data_a /= data_a.sum()
data_b /= data_b.sum()


class SegregationIndicesTest(unittest.TestCase):
    def test_km_identical(self):
        self.assertEqual(si.km(data_a), si.km(data_a))

    def test_km_total_segregation(self):
        self.assertAlmostEqual(si.km(data_b), 1)

    def test_km_no_segregation(self):
        self.assertAlmostEqual(si.km(data_a), 0)


if __name__ == '__main__':
    unittest.main()
