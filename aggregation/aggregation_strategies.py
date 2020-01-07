import os
from pathlib import Path

import pandas as pd
import geopandas as gpd

from spatial_segregation.analysis import plot_density, kernel_density_surface


if __name__ == '__main__':
    data_dir = Path('../data/')
    points = gpd.read_file(data_dir / 'points1878.shp')
    pop_by_plot = pd.read_excel(data_dir / 'pop_by_plot_1880.xlsx')
    pop_by_page = pd.read_excel(data_dir / 'pop_by_page_1880.xlsx')
    pop_by_district = pd.read_excel(data_dir / 'pop_by_district_1880.xlsx')
    # todo combinations

    plots_surface = kernel_density_surface()
    # todo kde + visualisation
