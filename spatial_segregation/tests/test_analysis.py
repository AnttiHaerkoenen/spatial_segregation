import unittest
import os

import pandas as pd
import pysal

from spatial_segregation import kde, data, segregation_indices, segregation_analysis

DATA_DIR = 'data'
N_SIMULATIONS = 10

os.chdir(os.path.pardir)
os.chdir(os.path.join(os.path.abspath(os.path.pardir), DATA_DIR))

v80 = data.aggregate_sum(data.reform(pd.read_csv('1880.csv', sep='\t')))
v00 = data.aggregate_sum(data.reform(pd.read_csv('1900.csv', sep='\t')))
v20 = data.aggregate_sum(data.reform(pd.read_csv('1920.csv', sep='\t')))

pop_data = {
    1880: v80,
    1900: v00,
    1920: v20
}

point_shp = pysal.open("points.shp")
point_db = pysal.open("points.dbf", 'r')

point_data = []
for i in range(len(point_shp)):
    point_data.append([point_db[i][0][1], point_shp[i][0], point_shp[i][1]])

cells = [i for i in range(15, 61, 15)]
bws = [i for i in range(20, 60)]

d = {year: data.add_coordinates(pop_data[year], point_data)
     for year in pop_data}


class TestAnalysis(unittest.TestCase):
    def test_analysis(self):
        ana = segregation_analysis.SegregationAnalysis(d[1880], 50, 50, 'distance_decay', 1)


class TestSimulation(unittest.TestCase):
    def test_simulation(self):
        ana = segregation_analysis.SegregationAnalysis(d[1880], 50, 50, 'distance_decay', 1)
        ana.simulate(N_SIMULATIONS)

    def test_simulations_empty(self):
        ana = segregation_analysis.SegregationAnalysis(d[1880], 50, 50, 'distance_decay', 1)
        self.assertTrue(ana.simulations.empty)

    def test_simulated_size(self):
        ana = segregation_analysis.SegregationAnalysis(d[1880], 50, 50, 'distance_decay', 1)
        ana.simulate(N_SIMULATIONS)
        self.assertEqual(ana.simulations.shape[0], N_SIMULATIONS)


if __name__ == '__main__':
    unittest.main()
