import os
import json

import pandas as pd
import matplotlib.pyplot as plt

from spatial_segregation import kde, data, segregation_indices, utils

DATA_DIR = 'data'


class SegregationAnalysis:
    def __init__(self, data_frame, cell_size, bw, kernel, which_indices='all', alpha=1, convex_hull=True, buffer=0):
        self.data = data_frame
        self.cell_size = cell_size
        self.kernel = kernel
        self.bw = round(bw * cell_size)
        self.alpha = alpha
        self.convex_hull=convex_hull
        self.buffer = buffer
        self.which_indices = which_indices

        self.surface = kde.create_kde_surface(
            self.data,
            self.cell_size,
            self.kernel,
            self.bw,
            self.alpha,
            self.convex_hull,
            self.buffer
        )
        print("KDE surface created (bandwidth={0}, cell size={1})".format(self.bw, self.cell_size))
        self.indices = segregation_indices.calc_indices(
            self.surface[['host', 'other']].values,
            which_indices=self.which_indices)

        self._simulations_list = []

    def __str__(self):
        strings = ["Spatial segregation analysis", ""]

        for k, v in self.param.items():
            strings.append("{0:>12}: {1:}".format(k, v))

        strings.append("")

        for i, v in self.indices.items():
            strings.append("{0:>12}: {1} p-value: {2} {3}".format(i, v, self.p[i], utils.get_stars(self.p[i])))

        return "\n".join(strings)

    def simulate(self, rep=500):
        self._simulations_list = []

        for _ in range(rep):
            data_frame = data.shuffle_data(self.data)
            kd = kde.create_kde_surface(
                data_frame,
                self.cell_size,
                self.kernel,
                self.bw,
                self.alpha,
                self.convex_hull,
                self.buffer
            )
            indices = segregation_indices.calc_indices(kd[['host', 'other']].values,
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
        n = self.simulations.shape[0]

        if n < 20:
            return {index: None for index in self.indices}

        for index, col in self.simulations.iteritems():
            greater = col > self.indices[index]
            p[index] = round(sum(greater.astype(int)) / n, 3)

        return p

    def plot(self, index='all', style='classic'):
        if len(self.simulations) == 0:
            raise ValueError("No simulations to plot")

        if index == 'all':
            pass
        elif index not in self.indices:
            raise ValueError("Index not computed.")

        plt.style.use(style)

        def plot_(i):
            self.simulations[i].plot.kde(color='red', label="simulated {0}".format(i))
            plt.axvline(self.indices[i], label="actual {0}".format(i))
            plt.legend()
            plt.title("Simulated {0} index distribution, n={1}".format(i, len(self.simulations)))

        if index == 'all':
            plt.subplot(221)
            plot_('km')
            plt.subplot(222)
            plot_('mi')
            plt.subplot(223)
            plot_('exposure')
            plt.subplot(224)
            plot_('isolation')
        else:
            plot_(index)

        plt.show()

    def plot_kde(self, style='classic'):
        plt.style.use(style)

        size = self.surface['host'] + self.surface['other']
        proportion = self.surface['other'] / size
        self.surface.plot.scatter(x='x', y='y', s=size, c=proportion)
        plt.title("KDE surface")
        plt.show()

########################################################################################################################


def main():
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))
    os.chdir(os.path.join(os.path.abspath(os.path.pardir), DATA_DIR))

    v80 = data.aggregate_sum(data.reform(pd.read_csv('1880.csv', sep='\t')))
    v00 = data.aggregate_sum(data.reform(pd.read_csv('1900.csv', sep='\t')))
    v20 = data.aggregate_sum(data.reform(pd.read_csv('1920.csv', sep='\t')))

    pop_data = {
        1880: v80,
        1900: v00,
        1920: v20
    }

    with open('points1878.geojson') as f:
        point_data = json.load(f)

    cells = [i for i in range(20, 81, 15)]
    bws = (1, 1.5, 2)

    d = {year: data.add_coordinates(pop_data[year], point_data)
         for year in pop_data}
    results = []

    ana = SegregationAnalysis(d[1880], 50, 1.5, 'distance_decay')
    ana.simulate(100)
    print(ana.simulations)
    print(ana)
    ana.plot_kde(style='ggplot')
    ana.plot(style='ggplot')

    # for y, d in d.items():
    #     for c in cells:
    #         for bw in bws:
    #             ana = SegregationAnalysis(d, c, bw, 'distance_decay', which_indices='km', buffer=20)
    #             ana.simulate(100)
    #             results.append({**ana.p,
    #                             **ana.param,
    #                             "year": y})
    #             # ana.plot_kde(style='ggplot')
    #
    # print(pd.DataFrame(results))


if __name__ == "__main__":
    main()
