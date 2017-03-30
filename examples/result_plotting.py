import os
import json

import pandas as pd
from pandas.tools.plotting import scatter_matrix
import matplotlib.pyplot as plt

from src import data, plotting

os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))
os.chdir(os.path.join(os.path.abspath(os.path.pardir), data.DATA_DIR))

pop_data = {
    '1880': data.aggregate_sum(data.reform(pd.read_csv('1880.csv'), districts='Valli')),
    '1900': data.aggregate_sum(data.reform(pd.read_csv('1900.csv'), districts='Valli')),
    '1920': data.aggregate_sum(data.reform(pd.read_csv('1920.csv'), districts='Valli'))
}

with open('points1878.geojson') as f:
    point_data = json.load(f)

cells = 25, 50, 75
bandwidths = 25, 50, 100, 150, 250

data = {year: data.add_coordinates(value, point_data, coordinates_to_meters=False)
        for year, value in pop_data.items()}

plotting.plot_densities_all(
    data,
    cell_size=50,
    bw=100,
    kernel='epanechnikov',
    subplot_title_param=dict(year='vuosi'),
    labels='luterilaiset ortodoksit erotus'.split(),
    title='Tiheys'
).set_facecolor('white')

results = pd.read_csv('kaikki.csv')
print(results)
corr_values = results.loc[:, lambda results: 's km exposure isolation information'.split()]
corr_values.columns = 'S D hPg gPg H'.split()
print(corr_values.corr(method='spearman'))

plt.style.use('ggplot')
scatter_matrix(corr_values, figsize=(10, 10), diagonal='kde')
plt.suptitle('Hajontamatriisi', size=20)
plt.show()
print(corr_values)
