import os

import pandas as pd
import geopandas as gpd

from spatial_segregation.analysis import plot_density, kernel_density_surface


if __name__ == '__main__':
    data_dir = '../data/'
    points = gpd.read_file(data_dir + 'points1878.shp')
    pop_by_plot = pd.read_csv(data_dir + '.csv')
    pop_by_page = pd.read_csv(data_dir + '.csv')
    pop_by_district = pd.read_csv(data_dir + '.csv')
    # todo combinations

    plots_surface = kernel_density_surface()
    # todo kde + visualisation
