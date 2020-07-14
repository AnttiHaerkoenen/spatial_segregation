import os
from pathlib import Path
from typing import Callable, Sequence
from itertools import product, chain
import random

import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import rasterio as rio
from scipy.spatial.distance import cdist
from segregation.aspatial import MinMax
from scipy import stats

from aggregation.distributions import Distribution, Gamma, BetaBinomial
from aggregation.aggregation_strategies import get_aggregate_locations_by_district

minority_locations = {
    'even': '011 016 021 026 031 036 041 046 051 056 '
            '061 071 076 081 086 091 096 101 '
            '111 121 126 131 136 141 '
            '151 161 166 171 176 181 186 191 '
            '201 211 216 221 226 231 236 241'.split(),
    'squares': '013 014 015 016 '
               '043 044 045 046 '
               '081 082 087 088 '
               '103 104 105 106 '
               '121 122 127 128 '
               '133 134 135 136 '
               '151 152 157 158 '
               '173 174 175 176 '
               '211 212 217 218 '
               '243 244 245 246'.split(),
    'side': '051 052 053 054 055 056 057 058 '
            '101 102 103 104 105 106 107 108 '
            '141 142 143 144 145 146 147 148 '
            '191 192 193 194 195 196 197 198 '
            '241 242 243 244 245 246 247 248'.split(),
    'ghetto': '081 082 083 084 085 086 087 088 '
              '091 092 093 094 095 096 097 098 '
              '131 132 133 134 135 136 137 138 '
              '171 172 173 174 175 176 177 178 '
              '181 182 183 184 185 186 187 188'.split(),
}

block_rows = [(1, 6), (6, 11), (11, 15), (15, 20), (20, 25)]
blocks = [f'{block:0>2}{plot}' for block in range(1, 25) for plot in range(1, 9)]

rows = list(chain.from_iterable([
    [f'{block:0>2}{plot}' for block in range(*row) for plot in range(1, 5)]
    + [f'{block:0>2}{plot}' for block in range(*row) for plot in range(8, 4, -1)]
    for row in block_rows
]))

snake = list(chain.from_iterable([
    [f'{block:0>2}{plot}' for block in range(*row) for plot in range(1, 5)]
    + [f'{block:0>2}{plot}' for block in range(*row) for plot in range(8, 4, -1)][::-1]
    for row in block_rows
]))

random.seed(123)
random_ = blocks.copy()
random.shuffle(random_)


def inverse_order(order: Sequence) -> list:
    new_order = sorted([(k, v) for k, v in enumerate(order)], key=lambda e: e[1])
    new_order = [e[0] for e in new_order]
    return new_order


orders = {
    'blocks': inverse_order(blocks),
    'rows': inverse_order(rows),
    'snake': inverse_order(snake),
    'random': inverse_order(random_),
}


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


def _get_simulated_plots_by_page(
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
        left -= plots

    return pages


def _get_simulated_pop_by_page(
        pop_by_plot: gpd.GeoDataFrame,
        plots_by_page: Sequence,
        page_col: str,
):
    page_nums = [[i] * n for i, n in enumerate(plots_by_page, start=1)]
    pop_by_plot[page_col] = list(chain.from_iterable(page_nums))
    pop_by_page = pop_by_plot.groupby(by=page_col).sum()

    return pop_by_page


def paginate(
        pop_by_plot: gpd.GeoDataFrame,
        order: Sequence,
        page_distribution: Distribution,
        page_col: str,
        n_plots: int = None,
):
    if not n_plots:
        n_plots = len(pop_by_plot.index)

    pages = _get_simulated_plots_by_page(page_distribution, n_plots)
    pop_by_plot = _get_simulated_pop_by_page(pop_by_plot, pages, page_col=page_col)
    pop_by_plot

    return pop_by_plot


def make_synthetic_data(
        locations: gpd.GeoDataFrame,
        minority_locations: Sequence,
        population_distribution: Distribution,
        number_col: str,
        minority_col: str,
        majority_col: str,
):
    pop_by_plot = locations.copy()

    numbers = locations[number_col]
    pop_by_plot[minority_col] = numbers.apply(
        lambda i: int(population_distribution.draw(1)[0]) if i in minority_locations else 0
    )
    pop_by_plot[majority_col] = numbers.apply(
        lambda i: int(population_distribution.draw(1)[0]) if i not in minority_locations else 0
    )

    return pop_by_plot


def aggregation_result(
        synthetic_plot_data: gpd.GeoDataFrame,
        page_distribution: Distribution,
        order: Sequence,
        number_col: str = 'number',
        page_col: str = 'page_number',
):
    synthetic_page_data = paginate(
        pop_by_plot=synthetic_plot_data,
        page_col=page_col,
        page_distribution=page_distribution,
        order=order,
    )
    print(synthetic_plot_data.describe())
    page_location_data = get_aggregate_locations_by_district(synthetic_page_data, location_data)


if __name__ == '__main__':
    data_dir = Path('../data')
    fig_dir = Path('../figures')

    locations = gpd.read_file(data_dir / 'simulated' / 'synthetic_district_plots.shp')
    pop_distribution = Gamma(shape=1.25, scale=8)
    page_distribution = BetaBinomial(n=28, a=3, b=12)

    data = make_synthetic_data(
        locations=locations,
        minority_locations=minority_locations['even'],
        population_distribution=pop_distribution,
        majority_col='lutheran',
        minority_col='orthodox',
        number_col='number',
    ).drop(columns='id')
    print(data.geometry)

    aggregated_results = aggregation_result(
        data,
        page_distribution,
        number_col='number',
        order=orders['random'],
    )
