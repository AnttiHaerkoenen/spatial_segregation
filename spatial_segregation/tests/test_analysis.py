import os
import json

import pandas as pd

from spatial_segregation import kde, data, segregation_indices, segregation_index_analysis

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

with open('points1878.geojson') as f:
    point_data = json.load(f)

cells = [i for i in range(15, 61, 15)]
bws = [i for i in range(20, 60)]

d = {year: data.add_coordinates(pop_data[year], point_data)
     for year in pop_data}
