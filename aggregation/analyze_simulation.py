from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.multivariate.pca import PCA
from statsmodels.sandbox.regression.predstd import wls_prediction_std

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


def plot_regression(
        ols_data,
        independent,
        dependent,
        fig_size,
        y_lim=(0, 1),
        x_lim=(0, 1),
):
    data = ols_data.sort_values(by=independent)
    ols_model = smf.ols(f'{dependent} ~ {independent}', data=data).fit()

    x = data[independent]
    y = data[dependent]

    pred_std, interval_l, interval_u = wls_prediction_std(ols_model)

    fig, ax = plt.subplots(figsize=fig_size)

    ax.plot(x, y, 'o')
    ax.plot(x, ols_model.fittedvalues, 'b-')
    ax.plot(x, interval_u, 'r-')
    ax.plot(x, interval_l, 'r-')

    # todo xlim & ylim

    return fig


if __name__ == '__main__':
    data_dir = Path('../data/simulated')

    data = load_data(data_dir, 'aggregation_effects_S_*.csv', index_col=0)
    data['level'] = data['level'].map(level_mapper)
    data = data[~data['order'].isin('random rows'.split())]
    data = data[data['level'] == 4]

    ax = plot_regression(
        data,
        independent='S_by_page',
        dependent='S_by_plot',
        fig_size=(8, 6),
    )

    plt.show()

    # pca_model = PCA(data, ncomp=4)
    # print(pca_model.loadings)

    # pca_model.plot_scree()
    # pca_model.plot_rsquare()
    # plt.show()
