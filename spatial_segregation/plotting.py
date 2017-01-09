import os

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from spatial_segregation import segregation_index_analysis, segregation_surface_analysis, data, kde, analyses


def plot_kernel(kernel, bw=1):
    """
    Function for plotting kernels.
    :param kernel: kernel function object
    :param bw: bw parameter
    :return: matplotlib.lines.Line2D object
    """
    x = np.arange(-2 * bw, 2 * bw, 0.01)
    y = [kernel(abs(x), bw) for x in np.nditer(x)]
    fig = plt.plot(x, y)
    return fig


def plot_results_all(results, kernel, indices=None, title=None, subplot_title_param=None, labels=None):
    bws = results['bw'].unique()
    cells = results['cell_size'].unique()
    years = results['year'].unique()
    fig, axs = plt.subplots(len(bws), len(cells), sharey='col')

    if not indices:
        indices = 's km exposure isolation'.split()

    if not title:
        title = "Kernel={0}".format(kernel)

    if not subplot_title_param:
        subplot_title_param = dict(bandwidth='bandwidth', cell_size='cell size')

    if not labels:
        labels = [i.capitalize() for i in indices]

    for i, b in enumerate(bws):
        for j, c in enumerate(cells):
            ax_data = results[(results.kernel == kernel) & (results.bw == b) & (results.cell_size == c)]
            ax_data = ax_data[['year'] + indices]
            ax_data = ax_data.set_index('year')
            axs[i, j].plot(ax_data)
            axs[i, j].set_xticks(years)
            subplot_title_param['b'] = b
            subplot_title_param['c'] = c
            axs[i, j].set_title("{bandwidth}={b}, {cell_size}={c}".format(**subplot_title_param), fontsize=12)

    fig.legend(labels=labels, loc='', fontsize=12)
    plt.suptitle(title, fontsize=18)

    return fig


if __name__ == '__main__':
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))
    os.chdir(os.path.join(os.path.abspath(os.path.pardir), data.DATA_DIR))

    results = pd.DataFrame.from_csv("kaikki.csv")
    plt.style.use("ggplot")

    otsikot = ["Martin et al.", "Gauss", "Epanechnikov", "Kolmio", "Laatikko"]
    for i, index in enumerate("distance_decay gaussian epanechnikov triangle uniform".split()):
        plot_results_all(
            results,
            index,
            indices="s km exposure isolation".split(),
            title=otsikot[i],
            subplot_title_param=dict(bandwidth='leveys', cell_size='solukoko'),
            labels="S K-M Exposure Isolation".split()
        )
        plt.show()
