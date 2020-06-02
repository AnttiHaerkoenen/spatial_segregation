import os
from pathlib import Path
from typing import Callable
from itertools import product

import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt

import rasterio as rio
from scipy.spatial.distance import cdist
from segregation.aspatial import MinMax

from aggregation.kernels import Martin, Quartic, Box, Triangle
from aggregation.aggregation_strategies import get_S, get_aggregate_locations
from spatial_segregation.analysis import plot_density, get_xy
from spatial_segregation.data import merge_dataframes,\
    split_plots, aggregate_sum, prepare_pop_data

if __name__ == '__main__':
    data_dir = Path('../data')
    fig_dir = Path('../figures')
