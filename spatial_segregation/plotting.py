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


def plot_results_all(results, kernel):
    bws = results['bw'].unique()
    cells = results['cell_size'].unique()
    fig, axs = plt.subplots(len(bws), len(cells))

    for i, b in enumerate(bws):
        for j, c in enumerate(cells):
            ax_data = results.where(results['bw', 'cell_size', 'kernel'] == b, c, kernel)
            axs[i, j].plot(ax_data)

    return fig

if __name__ == '__main__':
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))
    os.chdir(os.path.join(os.path.abspath(os.path.pardir), data.DATA_DIR))

    ana1 = analyses.SegregationIndexAnalyses()
    ana1.load("SegregationIndexAnalysis_kaikki.csv")
    print(ana1.results)

    ana2 = analyses.SegregationSurfaceAnalyses()
    ana2.load("SegregationSurfaceAnalysis_kaikki.csv")
    print(ana2.results)

    ana = pd.merge(ana1.results, ana2.results, on=['bw', 'cell_size'])
    plot_results_all(ana, 'distance_decay')
    plt.show()