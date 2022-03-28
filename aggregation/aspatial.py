from pathlib import Path

import pandas as pd
import numpy as np


def min_max(data, group_pop_var, total_pop_var):
    data = data.rename(columns={group_pop_var: 'group_pop_var',
                                total_pop_var: 'total_pop_var'})

    data['group_2_pop_var'] = data['total_pop_var'] - data['group_pop_var']

    data['group_1_pop_var_norm'] = data['group_pop_var'] / data['group_pop_var'].sum()
    data['group_2_pop_var_norm'] = data['group_2_pop_var'] / data['group_2_pop_var'].sum()

    density_1 = data['group_1_pop_var_norm'].values
    density_2 = data['group_2_pop_var_norm'].values
    densities = np.vstack([
        density_1,
        density_2
    ])
    v_union = densities.max(axis=0).sum()
    v_intersect = densities.min(axis=0).sum()

    S = 1 - v_intersect / v_union

    return S


def prepare_pop_data(
        population_data: pd.DataFrame,
        num_cols=None,
) -> pd.DataFrame:
    pop_frame = population_data.fillna(value=0)

    if not num_cols:
        num_cols = [
            'total_men',
            'total_women',
            'orthodox',
            'other_christian',
            'other_religion',
        ]

    pop_frame.loc[:, num_cols] = pop_frame.loc[:, num_cols].astype(int)
    pop_frame['lutheran'] = pop_frame['total_men'] \
        + pop_frame['total_women'] \
        - pop_frame['orthodox'] \
        - pop_frame['other_christian'] \
        - pop_frame['other_religion']

    return pop_frame


if __name__ == '__main__':
    data_dir = Path('../data')
    fig_dir = Path('../figures')

    district_codes = pd.read_csv(data_dir / 'district_codes_1878.csv')
    district_codes = {k: v for k, v in district_codes.itertuples(index=False)}

    pop_by_plot = pd.read_csv(data_dir / 'interim' / 'pop_by_plot_1880.csv').pipe(prepare_pop_data)
    pop_by_plot['plot_number'] = [str(n).split(',')[0] for n in pop_by_plot['plot_number']]
    pop_by_plot.drop(columns=['Unnamed: 0',], inplace=True)
    pop_by_plot['total'] = pop_by_plot['total_men'] + pop_by_plot['total_women']
    pop_by_district = pop_by_plot.groupby('district').sum()
    print(pop_by_district.columns)
    S = round(min_max(pop_by_district, 'orthodox', 'total'), 3)
    print(S)  # 0.358
