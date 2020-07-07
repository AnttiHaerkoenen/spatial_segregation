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

from aggregation.distributions import Distribution


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

    print([len(k) for k in minority_locations.values()])
