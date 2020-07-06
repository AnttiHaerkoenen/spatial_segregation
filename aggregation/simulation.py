import os
from pathlib import Path
from typing import Callable, Sequence
from itertools import product

import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt

import rasterio as rio
from scipy.spatial.distance import cdist
from segregation.aspatial import MinMax
from scipy import stats

from aggregation.kernels import Martin, Quartic, Box, Triangle
from aggregation.aggregation_strategies import get_S, get_aggregate_locations, get_multiple_S
from aggregation.distributions import Distribution
from spatial_segregation.analysis import plot_density, get_xy


def simulate_pop_by_page(
        page_distribution: Distribution,
        plot_distribution: Distribution,
        n_plots: int,
):
    left = n_plots
    pages = []

    while left > 0:
        plots = page_distribution.draw(1)[0]

        if plots > left:
            plots = left

        pop = sum(plot_distribution.draw(plots))
        pages.append(pop)

    return pages


def simulate_plots_by_page(
        page_distribution: Distribution,
        n_plots: int,
):
    left = n_plots
    pages = []

    while left > 0:
        plots = page_distribution.draw(1)[0]

        if plots > left:
            plots = left

        pages.append(plots)

    return pages


def get_simulated_pop_by_page(
        pop_by_plot: gpd.GeoDataFrame,
        plots_by_page: Sequence,
):
    pop_by_plot['page_num'] = [[i] * n for i, n in enumerate(plots_by_page, start=1)]
    pop_by_page = pop_by_plot.groupby(by='page_num').sum()

    return pop_by_page


if __name__ == '__main__':
    data_dir = Path('../data')
    fig_dir = Path('../figures')
    beta_binom_data = pd.Series(stats.distributions.betabinom.rvs(28, 3, 12, size=1000))
