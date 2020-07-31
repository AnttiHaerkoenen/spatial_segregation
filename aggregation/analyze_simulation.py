from pathlib import Path
from itertools import product

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import cm
import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.multivariate.pca import PCA
from statsmodels.sandbox.regression.predstd import wls_prediction_std
from statsmodels.graphics.agreement import mean_diff_plot
from statsmodels.graphics.regressionplots import plot_regress_exog

level_mapper = {k: v for v, k in enumerate('even even-squares squares squares-side side ghetto'.split())}


def load_data(
        data_dir: Path,
        pattern: str,
        **kwargs
):
    files = data_dir.glob(pattern=pattern)

    results = []

    for f in files:
        s_loc = f.stem.rfind('_S_')
        order = f.stem[s_loc + 3:]
        order_data = pd.read_csv(f, **kwargs)
        order_data['order'] = order
        results.append(order_data)

    data = pd.concat(results)
    data = data.reset_index().drop(columns='index')
    return data


def get_multiple_corrected_S(data):
    bandwidths = data['bandwidth'].unique()
    cells = data['cell'].unique()
    functions = data['function'].unique()
    orders = data['order'].unique()

    results = []

    for o, f, bw, c in product(orders, functions, bandwidths, cells):
        case_data = data[
            (data.order == o) &
            (data.function == f) &
            (data.bandwidth == bw) &
            (data.cell == c)
        ]
        ols_model = smf.ols('S_by_plot ~ S_by_page', data=case_data).fit()

        a, b = ols_model.params
        results.append({
            'a': a,
            'b': b,
            'bandwidth': bw,
            'cell': c,
            'function': f,
            'order': o,
        })

    return pd.DataFrame(results).sort_values(by='b').reset_index(drop=True)


if __name__ == '__main__':
    data_dir = Path('../data/simulated')

    data = load_data(data_dir, 'aggregation_effects_S_*.csv', index_col=0)
    data['level'] = data['level'].map(level_mapper)

    data = data[data['order'].isin('blocks'.split())]
    # data = data[data['function'].isin('Martin_et_al_2000'.split())]
    data = data[data['level'].isin([0, 1, 2, 3, 4])]
    # data = data[data['bandwidth'] == 100]
    # data = data[data['cell'] == 25]

    results = get_multiple_corrected_S(data)
    print(results.describe())
    print(results)
    results.hist(column='a')
    results.hist(column='b')
    plt.show()

    # data['S_corrected'] = 1.1718 * data['S_by_page'] - 0.0201
    # data['S_difference_corrected'] = data['S_corrected'] - data['S_by_plot']

    # ols_model = smf.ols('S_by_plot ~ S_corrected', data=data).fit()
    # print(ols_model.summary())

    # plot_regress_exog(ols_model, 'S_corrected')
    # data['S_difference_corrected'].hist()
    # data.plot(
    #     x='S_corrected',
    #     y='S_by_plot',
    #     c='level',
    #     kind='scatter',
    #     cmap=cm.get_cmap('viridis', 5),
    # )
    # mean_diff_plot(data['S_by_plot'], data['S_corrected'], sd_limit=3)
    # plt.show()
