from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.multivariate.pca import PCA

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


if __name__ == '__main__':
    data_dir = Path('../data/simulated')

    order = 'snake'
    data = pd.read_csv(
        data_dir / f'aggregation_effects_S_{order}.csv', index_col=0)
    data['level'] = data['level'].map(level_mapper)
    data.drop(columns='function S_difference'.split(), inplace=True)

    data = load_data(data_dir, 'aggregation_effects_S_*.csv', index_col=0)
    print(data)

    # ols_model = smf.ols('S_by_page ~ S_by_plot + level', data=data).fit()
    # print(ols_model.summary())
    # print(ols_model.predict(exog=dict(S_by_plot=0.5)))
    #
    # pca_model = PCA(data, ncomp=4)
    # print(pca_model.loadings)

    # pca_model.plot_scree()
    # pca_model.plot_rsquare()
    # plt.show()
