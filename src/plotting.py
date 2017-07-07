import os

import numpy as np
import pandas as pd
from pandas.tools.plotting import scatter_matrix
import matplotlib.pyplot as plt

import segregation_index_analysis, segregation_surface_analysis, data, kde, analyses, utils


def plot_kernel(kernel, bw=1):
    """
    Function for plotting kernels.
    :param kernel: kernel function object
    :param bw: bw parameter
    :return: matplotlib.lines.Line2D object
    """
    x = np.arange(-2 * bw, 2 * bw, 0.01)
    y = kernel(np.abs(x), bw)
    fig = plt.plot(x, y)
    return fig


def plot_results_all(results, kernel, indices=None, title=None, subplot_title_param=None, labels=None):
    bws = sorted(results['bw'].unique())
    cells = sorted(results['cell_size'].unique())
    years = sorted(results['year'].unique())
    fig, axs = plt.subplots(len(bws), len(cells), sharey='col', figsize=(8, 12))

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

    axs[0, 0].legend(
        labels=labels,
        fontsize=10,
        bbox_to_anchor=(0, 1.1),
        ncol=2,
        loc=3
    ).get_frame().set_facecolor('white')
    plt.suptitle(title, fontsize=22)

    for ax, c in zip(axs[0], cells):
        ax.set_title('{0}'.format(c), size=14)
    for ax, bw in zip(axs[:, 0], bws):
        ax.set_ylabel(bw, size=14)

    axs[0, len(cells) // 2].annotate(
        subplot_title_param['cell_size'].capitalize(),
        (0.5, 1),
        xytext=(0, 20),
        textcoords='offset points',
        xycoords='axes fraction',
        ha='center',
        va='bottom',
        size=18
    )

    axs[len(bws) // 2, 0].annotate(
        subplot_title_param['bandwidth'].capitalize(),
        (0, 0.5),
        xytext=(-50, 0),
        textcoords='offset points',
        xycoords='axes fraction',
        ha='right',
        va='center',
        size=18, rotation=90
    )

    return fig


def plot_densities_all(pop_data, cell_size, bw, kernel, title=None, subplot_title_param=None, labels=None):
    fig, axs = plt.subplots(len(pop_data), 3, sharey='col', figsize=(8, 8))

    if not title:
        title = "Kernel={0}".format(kernel)

    if not subplot_title_param:
        subplot_title_param = dict(year='year')

    if not labels:
        labels = 'host', 'other', 'difference'

    for i, year in enumerate(sorted(pop_data)):
        surface = segregation_surface_analysis.SegregationSurfaceAnalysis(
            pop_data[year],
            cell_size=cell_size,
            bw=bw,
            kernel=kernel
        ).surface
        axs[i, 0].matshow(surface['host']).set_cmap('gray_r')
        axs[i, 1].matshow(surface['other']).set_cmap('gray_r')
        axs[i, 2].matshow(surface['host'] - surface['other']).set_cmap('hot')

        for j in range(3):
            axs[i, j].set_xticklabels([])
            axs[i, j].set_yticklabels([])

    plt.suptitle(title, fontsize=22)

    for ax, l in zip(axs[0], labels):
        ax.set_title('{0}'.format(l), size=14)
    for ax, y in zip(axs[:, 0], sorted(pop_data)):
        ax.set_ylabel(y, size=14)

    axs[len(pop_data) // 2, 0].annotate(
        subplot_title_param['year'].capitalize(),
        (0, 0.5),
        xytext=(-50, 0),
        textcoords='offset points',
        xycoords='axes fraction',
        ha='right',
        va='center',
        size=18,
        rotation=90
    )

    return fig


def plot_density(kdesurface, group):
    fig = plt.matshow(kdesurface[group])
    fig.set_cmap('gray_r')
    return fig


def plot_diff(kdesurface, group1='host', group2='other'):
    fig = plt.matshow(kdesurface[group1] - kdesurface[group2])
    fig.set_cmap('gray_r')
    return fig


if __name__ == '__main__':
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))
    os.chdir(os.path.join(os.path.abspath(os.path.pardir), data.DATA_DIR))

    results = pd.DataFrame.from_csv("kaikki.csv")
    plt.style.use("ggplot")
    scatter_matrix(results["s km exposure isolation information".split()], diagonal='kde', figsize=(10, 8))
    plt.suptitle("Indeksien välinen korrelaatio", fontsize=18)
    plt.show()

    ytimet = ["Kaksipainoinen", "Gauss", "Epanechnikov", "Kolmio", "Laatikko"]
    for i, index in enumerate("biweight gaussian epanechnikov triangle uniform".split()):
        plot_results_all(
            results,
            index,
            indices="s km exposure isolation information".split(),
            title=ytimet[i],
            subplot_title_param=dict(bandwidth='leveys', cell_size='solukoko'),
            labels="S D hPg gPg H".split()
        )
        plt.show()
