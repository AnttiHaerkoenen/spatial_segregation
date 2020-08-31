import os
from pathlib import Path
from typing import Callable, Sequence
from itertools import product, chain
import random

import geopandas as gpd
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from aggregation.kernels import Martin, Quartic, Box, Triangle
from aggregation.distributions import Distribution, Gamma, BetaBinomial
from aggregation.aggregation_strategies import get_aggregate_locations_by_district, get_multiple_S


district_locs = {
    '1': {'xoff': -1100, 'yoff': -720},
    '2': {'xoff': 0, 'yoff': -720},
    '3': {'xoff': 1100, 'yoff': -720},
    '4': {'xoff': -1100, 'yoff': 0},
    '5': {'xoff': 0, 'yoff': 0},
    '6': {'xoff': 1100, 'yoff': 0},
    '7': {'xoff': -1100, 'yoff': 720},
    '8': {'xoff': 0, 'yoff': 720},
    '9': {'xoff': 1100, 'yoff': 720},
}

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
}

minority_locations = {
    k: [(d, plot) for d in district_locs for plot in v]
    for k, v
    in minority_locations.items()
}
minority_locations['ghetto'] = [
    (d, plot)
    for d in '3 6 9'.split()
    for plot in [
        f'{block:0>2}{p}'
        for block in chain(
            range(2, 6),
            range(8, 11),
            range(13, 15),
            range(17, 20),
            range(22, 25),
        )
        for p in range(1, 9)
    ]
]

minority_locations['even-squares'] = minority_locations['even'][:240]\
                                     + minority_locations['squares'][240:]
minority_locations['squares-even'] = minority_locations['squares'][:240]\
                                     + minority_locations['even'][240:]

minority_locations['squares-side'] = minority_locations['squares'][:240]\
                                     + minority_locations['side'][240:]
minority_locations['side-squares'] = minority_locations['side'][:240]\
                                     + minority_locations['squares'][240:]

minority_locations['side-ghetto'] = minority_locations['side'][:240] \
                                    + minority_locations['ghetto'][240:]
minority_locations['ghetto-side'] = minority_locations['ghetto'][:240] \
                                    + minority_locations['side'][240:]

minority_locations['squares-side-ghetto'] = minority_locations['squares'][:120] \
                                            + minority_locations['side'][120:240] \
                                            + minority_locations['ghetto'][240:]

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


orders = dict(
    blocks=blocks,
    rows=rows,
    snake=snake,
    random=random_,
)
orders['snake_20'] = orders['snake'][:40] + orders['blocks'][40:]
orders['snake_40'] = orders['snake'][:80] + orders['blocks'][80:]
orders['snake_60'] = orders['snake'][:112] + orders['blocks'][112:]
orders['snake_80'] = orders['snake'][:152] + orders['blocks'][152:]

orders = {k: inverse_order(v) for k, v in orders.items()}

assert all([len(v) == 360 for v in minority_locations.values()])
assert all([len(v) == 192 for v in orders.values()])


# def simulate_pop_by_page(
#         page_distribution: Distribution,
#         plot_distribution: Distribution,
#         n_plots: int,
# ):
#     left = n_plots
#     pages = []
#
#     while left > 0:
#         plots = page_distribution.draw(1)[0]
#
#         if plots > left:
#             plots = left
#
#         pop = sum(plot_distribution.draw(plots))
#         pages.append(pop)
#
#     return pages


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


def _get_representative_plot(
        plots_in_page,
        plot_number_col,
        district_number_col,
        how,
):
    assert how in {'first', 'mid', 'last'}

    if how == 'mid':
        midpoint = plots_in_page.index[len(plots_in_page.index) // 2]
        return plots_in_page.loc[midpoint, [district_number_col, plot_number_col]]
    elif how == 'first':
        first = plots_in_page.index[0]
        return plots_in_page.loc[first, [district_number_col, plot_number_col]]
    elif how == 'last':
        last = plots_in_page.index[-1]
        return plots_in_page.loc[last, [district_number_col, plot_number_col]]


def _get_simulated_pop_by_page(
        pop_by_plot: gpd.GeoDataFrame,
        plots_by_page: Sequence,
        page_col: str,
        plot_number_col: str,
        district_number_col: str,
):
    page_nums = [[i] * n for i, n in enumerate(plots_by_page, start=0)]
    pop_by_plot[page_col] = list(chain.from_iterable(page_nums))
    pop_by_page = pop_by_plot.groupby(by=page_col).sum()

    representative_plots_and_districts = pop_by_plot.groupby(by=page_col).apply(
        _get_representative_plot,
        plot_number_col=plot_number_col,
        how='mid',
        district_number_col=district_number_col,
    )

    assert len(representative_plots_and_districts.index) == len(pop_by_page.index)
    pop_by_page[plot_number_col] = representative_plots_and_districts[plot_number_col]
    pop_by_page[district_number_col] = representative_plots_and_districts[district_number_col]

    return pop_by_page


def paginate(
        pop_by_plot: gpd.GeoDataFrame,
        order: Sequence,
        page_distribution: Distribution,
        page_col: str,
        plot_number_col: str,
        district_number_col: str,
        n_plots: int = None,
):
    if not n_plots:
        n_plots = len(pop_by_plot.index)

    if order:
        if n_plots % len(order) != 0:
            raise ValueError('orders and plots do not match')

        pop_by_plot['order'] = order
        pop_by_plot.sort_values(by='district order'.split(), inplace=True)
        pop_by_plot.drop(columns='order', inplace=True)

    pages = _get_simulated_plots_by_page(page_distribution, n_plots)
    pop_by_page = _get_simulated_pop_by_page(
        pop_by_plot,
        pages,
        page_col=page_col,
        plot_number_col=plot_number_col,
        district_number_col=district_number_col,
    )

    return pop_by_page


def make_synthetic_data(
        locations: gpd.GeoDataFrame,
        minority_locations: Sequence[tuple],
        population_distribution: Distribution,
        id_cols: Sequence,
        minority_col: str,
        majority_col: str,
        total_col: str,
):
    pop_by_plot = locations.copy()

    numbers = locations.loc[:, id_cols]

    pop_by_plot[minority_col] = numbers.apply(
        lambda i: int(population_distribution.draw(1)[0]) if tuple(i) in minority_locations else 0,
        axis=1,
    )
    pop_by_plot[majority_col] = numbers.apply(
        lambda i: int(population_distribution.draw(1)[0]) if tuple(i) not in minority_locations else 0,
        axis=1,
    )
    pop_by_plot[total_col] = pop_by_plot[minority_col] + pop_by_plot[majority_col]

    return pop_by_plot


def make_synthetic_datasets(
        n=1,
        **kwargs
):
    datasets = []
    print("Making simulated datasets", end='')

    for i in range(n):
        print(".", end='')

        plot_data = make_synthetic_data(**kwargs).drop(columns='id')
        datasets.append(plot_data)

    print()

    return datasets


def aggregation_result(
        synthetic_plot_data: gpd.GeoDataFrame,
        page_distribution: Distribution,
        order: Sequence,
        plot_number_col: str = 'number',
        district_number_col: str = 'district',
        page_col: str = 'page_number',
        use_actual_plots: bool = True,
):
    location_data = synthetic_plot_data.loc[:, ['geometry', district_number_col, plot_number_col]]

    synthetic_page_data = paginate(
        pop_by_plot=synthetic_plot_data,
        order=order,
        page_distribution=page_distribution,
        page_col=page_col,
        plot_number_col=plot_number_col,
        district_number_col=district_number_col
    )

    if use_actual_plots:
        location_data = location_data.set_index([district_number_col, plot_number_col])
        synthetic_page_data = synthetic_page_data.set_index([district_number_col, plot_number_col])
        page_location_data = location_data.join(synthetic_page_data, on=[district_number_col, plot_number_col])
        page_location_data.dropna(axis=0, inplace=True)
    else:
        synthetic_page_data.drop(columns=[plot_number_col], inplace=True)
        page_location_data = get_aggregate_locations_by_district(
            synthetic_page_data,
            location_data,
        )

    return page_location_data


def simulate_multiple_segregation_levels(
        locations,
        minority_location_dict,
        order,
        page_distribution: Distribution,
        population_distribution: Distribution,
        majority_col='lutheran',
        minority_col='orthodox',
        total_col='total',
        plot_number_col='number',
        id_cols=('district', 'number'),
        use_actual_plots=True,
        n: int = 1,
        **kwargs
) -> pd.DataFrame:

    print(f"Simulating multiple segregation levels")

    results = []

    for k, v in minority_location_dict.items():
        print(f"Simulating segregation with minority locations set to '{k}'")

        synthetic_datasets = make_synthetic_datasets(
            n=n,
            locations=locations,
            minority_locations=v,
            population_distribution=population_distribution,
            majority_col=majority_col,
            minority_col=minority_col,
            total_col=total_col,
            id_cols=id_cols,
        )

        print('Simulating page-based aggregation', end='')

        for i in range(n):
            plot_data = synthetic_datasets[i]

            page_data = aggregation_result(
                plot_data,
                page_distribution,
                plot_number_col=plot_number_col,
                order=order,
                use_actual_plots=use_actual_plots,
            )

            multiple_S = get_multiple_S(
                datasets={
                    'page_data': page_data,
                    'plot_data': plot_data,
                },
                **kwargs
            )
            multiple_S['level'] = k
            results.append(multiple_S)

            print(".", end='')

        print()

    print("Multiple segregation levels analysis finished.")

    return pd.concat(results, axis=0).reset_index(drop=True)


def clone_district(
        locations: gpd.GeoDataFrame,
        district_locs: dict,
) -> gpd.GeoDataFrame:
    districts = []

    for d, offsets in district_locs.items():
        new_locs = locations.copy()
        new_locs['district'] = d
        new_locs.geometry = locations.geometry.translate(**offsets)
        districts.append(new_locs)

    districts = pd.concat(districts).reset_index(drop=True)
    return districts


if __name__ == '__main__':
    data_dir = Path('../data')
    fig_dir = Path('../figures')

    locations = gpd.read_file(data_dir / 'simulated' / 'synthetic_district_plots.shp')
    locations.geometry = locations.geometry.centroid
    locations = clone_district(locations, district_locs)

    orders = {k: v * len(district_locs) for k, v in orders.items()}

    pop_distribution = Gamma(shape=1.25, scale=8)
    page_distribution = BetaBinomial(n=28, a=3, b=12)

    kwargs = {
        'bandwidths': [100, 150, 200, 250, 300, 400, 500],
        'cell_sizes': [25, 50],
        'kernel_functions': [Martin, Triangle, Box],
    }

    for k, v in orders.items():
        print()
        print(k.upper())
        print()

        simulation_results = simulate_multiple_segregation_levels(
            locations=locations,
            minority_location_dict=minority_locations,
            order=v,
            population_distribution=pop_distribution,
            page_distribution=page_distribution,
            n=20,
            **kwargs
        )

        simulation_results.to_csv(data_dir / 'simulated' / f'aggregation_effects_S_{k}.csv')

        print(k.upper())
        print(simulation_results.describe())
