import os
import json
import datetime

import pandas as pd
import matplotlib.pyplot as plt

from spatial_segregation import analyses, kde, data, segregation_indices, utils
from spatial_segregation.exceptions import SegregationIndexAnalysisException


class SegregationIndexAnalysis:
    def __init__(self,
                 data_dict,
                 cell_size,
                 bw,
                 kernel,
                 which_indices='all',
                 alpha=1,
                 convex_hull=True,
                 buffer=0,
                 data_id=None,
                 groups=("host", "other")):
        self.data = data_dict
        self.cell_size = cell_size
        self.kernel = kernel
        self.bw = bw
        self.alpha = alpha
        self.convex_hull = convex_hull
        self.buffer = buffer
        self.which_indices = which_indices
        self.data_id = data_id
        self.groups = groups

        self.surface = kde.KernelDensitySurface(
            self.data,
            groups=groups,
            cell_size=self.cell_size,
            kernel=self.kernel,
            bw=self.bw,
            a=self.alpha,
            convex_hull=self.convex_hull,
            convex_hull_buffer=self.buffer
        )

        self.indices = segregation_indices.calc_indices(
            self.surface.population_values,
            which_indices=self.which_indices
        )

        self._simulations_list = []

    def __str__(self):
        strings = ["Spatial segregation analysis", ""]

        if self.data_id:
            strings.append("Data: {0}".format(self.data_id))

        for k, v in self.param.items():
            strings.append("{0:>12}: {1:}".format(k, v))

        strings.append("")

        for i, v in self.indices.items():
            strings.append("{0:>12}: {1}".format(i, v))

        return "\n".join(strings)

    def simulate(self, rep=500):
        self._simulations_list = []

        for _ in range(rep):
            data_frame = data.shuffle_data(self.data)
            kd = kde.KernelDensitySurface(
                data_frame,
                cell_size=self.cell_size,
                kernel=self.kernel,
                bw=self.bw,
                a=self.alpha,
                convex_hull=self.convex_hull,
                convex_hull_buffer=self.buffer,
                groups=self.groups
            )
            indices = segregation_indices.calc_indices(kd.population_values,
                                                       which_indices=self.which_indices)

            self._simulations_list.append(indices)

        print("Simulation complete (n={0})".format(rep))

    @property
    def param(self):
        param = {
            'cell size': self.cell_size,
            'bandwidth': self.bw,
            'kernel': self.kernel,
            'convex hull': self.convex_hull
        }

        if self.kernel == 'distance_decay':
            param['alpha'] = self.alpha

        if self.convex_hull:
            param['buffer'] = self.buffer

        return param

    @property
    def simulations(self):
        return pd.DataFrame(self._simulations_list)

    @property
    def p(self):
        p = dict()
        n = len(self._simulations_list)

        if n < 10:
            return dict()

        for index, col in self.simulations.iteritems():
            greater = col > self.indices[index]
            p_val = sum(greater.astype(int)) / n
            p["p_{0}".format(index)] = round(p_val, 3)

        return p

    def plot(self, index):
        if len(self.simulations) == 0:
            raise ValueError("No simulations to plot")

        if index not in self.indices:
            raise ValueError("Index not computed.")

        fig = self.simulations[index].plot.kde(color='red', label="simulated {0}".format(index))
        fig.axvline(self.indices[index], label="actual {0}".format(index))
        fig.legend()
        fig.set_title("Simulated {0} index distribution, n={1}".format(index, len(self.simulations)))
        return fig


########################################################################################################################


if __name__ == '__main__':
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))
    os.chdir(os.path.join(os.path.abspath(os.path.pardir), data.DATA_DIR))

    v80 = data.aggregate_sum(data.reform(pd.read_csv('1880.csv')))
    v00 = data.aggregate_sum(data.reform(pd.read_csv('1900.csv')))
    v20 = data.aggregate_sum(data.reform(pd.read_csv('1920.csv')))

    pop_data = {
        1880: v80,
        1900: v00,
        1920: v20
    }

    with open('points1878.geojson') as f:
        point_data = json.load(f)

    cells = [i for i in range(20, 81, 20)]
    bws = (1.5, 2, 2.5)

    d = {year: data.add_coordinates(pop_data[year], point_data, coordinates_to_meters=False)
         for year in pop_data}

    ana = SegregationIndexAnalysis(d[1880], 50, 1.5, 'distance_decay')
    ana.simulate(100)
    print(ana.simulations)
    print(ana)
    ana.plot("km")
    plt.show()

    # ana = analyses.SegregationIndexAnalyses(d, cell_sizes=cells, bws=bws, kernels=("uniform", "distance_decay"), simulations=49)
    # print(ana.results)
    # ana.save()
