import os
import json

import pandas as pd
import numpy as np

from old.src import kde, parameters, analyses, data

os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))
os.chdir(os.path.join(os.path.abspath(os.path.pardir), data.DATA_DIR))

pop_data = {
    '1880': data.SpatialSegregationData._aggregate_sum(
        data.SpatialSegregationData.reform_pop_data(pd.read_csv('1880.csv'),
                                                    districts='Valli')),
    '1900': data.SpatialSegregationData._aggregate_sum(
        data.SpatialSegregationData.reform_pop_data(pd.read_csv('1900.csv'),
                                                    districts='Valli')),
    '1920': data.SpatialSegregationData._aggregate_sum(
        data.SpatialSegregationData.reform_pop_data(pd.read_csv('1920.csv'),
                                                    districts='Valli'))
}

with open('points1878.geojson') as f:
    point_data = json.load(f)

cells = 25, 50, 75
bandwidths = 25, 50, 100, 150, 250
pars = parameters.Parameters(
    cell_sizes=cells,
    kernels=kde.KERNELS,
    bws=bandwidths,
    alphas=(1,)
)

data = {year: data.SpatialSegregationData._combine_data(value, point_data, coordinates_to_meters=False)
        for year, value in pop_data.items()}

ana1 = analyses.SegregationSurfaceAnalyses(
    data_dict=data,
    parameters=pars
)
ana1.analyse()
ana1.save("SegregationSurfaceAnalysis_kaikki.csv")

ana2 = analyses.SegregationIndexAnalyses(
    data_dict=data,
    parameters=pars
)
ana2.analyse()
ana2.save("SegregationIndexAnalysis_kaikki.csv")

results = pd.merge(ana1.results, ana2.results)
results = results["year kernel bandwidth cell_size s exposure isolation km information".split()]
results = results.sort_values(by='year bandwidth cell_size kernel'.split())
results.index = np.arange(1, len(results) + 1)

results.to_csv("kaikki.csv")
