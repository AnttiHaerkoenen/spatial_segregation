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

level_mapper = {
    k: v for v, k in enumerate(
        [
            'even',
            'even-squares',
            'squares-even',
            'squares',
            'squares-side',
            'even-squares-ghetto',
            'squares-ghetto',
            'side-squares',
            'squares-side-ghetto',
            'ghetto-squares',
            'side',
            'side-ghetto',
            'ghetto-side',
            'ghetto',
        ],
        start=1,
    )
}


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
    levels = data['level'].unique()

    results = []

    for o, f, bw, c, l in product(orders, functions, bandwidths, cells, levels):
        case_data = data[
            (data.order == o) &
            (data.function == f) &
            (data.bandwidth == bw) &
            (data.cell == c) &
            (data.level == l)
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
            'level': l,
        })

    return pd.DataFrame(results).sort_values(by='b').reset_index(drop=True)


if __name__ == '__main__':
    data_dir = Path('../data/simulated') / 'actual_plots'

    data = load_data(data_dir, 'aggregation_effects_S_*.csv', index_col=0)
    data['level'] = data['level'].map(level_mapper)

    data = data[data['order'].isin('blocks snake_20 snake_40 snake_60 snake_80 snake'.split())]
    data = data[data['function'].isin('Martin_et_al_2000'.split())]
    data = data[data['level'].isin([v for k, v in level_mapper.items() if 'side' not in k])]
    data = data[data['bandwidth'] == 200]
    # data = data[data['cell'] == 25]

    # data['S_corrected'] = 1.1718 * data['S_by_page'] - 0.0201
    # data['S_difference_corrected'] = data['S_corrected'] - data['S_by_plot']

    ols_model = smf.ols('S_by_plot ~ S_by_page', data=data).fit()
    print(ols_model.summary())
    # data.plot(kind='scatter', x='S_by_page', y='S_by_plot', c='level')
    data.boxplot(column='S_by_plot', by='level')
    data.boxplot(column='S_by_page', by='level')

    # plot_regress_exog(ols_model, 'S_corrected')
    # data['S_difference_corrected'].hist()
    data.plot(
        x='S_by_page',
        y='S_by_plot',
        c='level',
        kind='scatter',
        cmap=cm.get_cmap('viridis', len(level_mapper)),
    )
    mean_diff_plot(data['S_by_plot'], data['S_by_page'], sd_limit=3)
    plt.show()
