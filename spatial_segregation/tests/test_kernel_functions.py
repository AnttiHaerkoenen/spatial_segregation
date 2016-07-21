import unittest
import random

import spatial_segregation.kernel_functions as kf

bw = random.randint(1, 10000)


class TestDistanceDecay(unittest.TestCase):
    def test_dd_zero(self):
        self.assertEqual(kf.distance_decay(bw + 1, bw), 0)
        self.assertEqual(kf.distance_decay(bw, bw), 0)

    def test_dd_center(self):
        self.assertEqual(kf.distance_decay(0, bw), 1)

    def test_dd_halfway(self):
        self.assertEqual(kf.distance_decay(bw / 2, bw), 0.6)


if __name__ == '__main__':
    unittest.main()
