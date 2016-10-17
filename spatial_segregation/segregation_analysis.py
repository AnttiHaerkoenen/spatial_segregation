import os
import json

import pandas as pd
import matplotlib.pyplot as plt

from spatial_segregation import kde, data, segregation_indices

DATA_DIR = 'data'


class SegregationAnalysis:
    def __init__(self, data_frame, cell_size, bw, kernel, alpha=1, convex_hull=True, buffer=0):
        self.data = data_frame
        self.cell_size = cell_size
        self.kernel = kernel
        self.bw = bw
        self.alpha = alpha
        self.convex_hull=convex_hull
        self.buffer = buffer

        self.surface = kde.create_kde_surface(
            self.data,
            self.cell_size,
            self.kernel,
            self.bw,
            self.alpha,
            self.convex_hull,
            self.buffer
        )
        self.indices = segregation_indices.calc_indices(self.surface[['host', 'other']].values)

        self._simulations_list = []

    def simulate(self, rep=1000):
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
            self._simulations_list.append(segregation_indices.calc_indices(kd[['host', 'other']].values))

    @property
    def simulations(self):
        return pd.DataFrame(self._simulations_list)

    def plot(self, index='km'):

        if len(self.simulations) == 0:
            raise ValueError("No simulations to plot")
        if index not in self.indices:
            raise ValueError("Index not calculated")

        self.simulations[index].plot.kde(color='red', label="simulated {0}".format(index))
        plt.axvline(self.indices[index], label="actual {0}".format(index))
        plt.legend()
        plt.title("Simulated {0} index distribution, n={1}".format(index, len(self.simulations)))
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

    cells = [i for i in range(15, 61, 15)]
    bws = [i for i in range(20, 60, 10)]

    d = {year: data.add_coordinates(pop_data[year], point_data)
         for year in pop_data}
    results = []

    ana = SegregationAnalysis(d[1880], 50, 50, 'distance_decay')
    ana.simulate(10)
    print(ana.simulations)
    ana.plot()

    # for y, d in d.items():
    #     for c in cells:
    #         for bw in bws:
    #             ana = SegregationAnalysis(d, c, bw, 'distance_decay')
    #             print(ana.indices)
    #             results.append(ana.indices)


if __name__ == "__main__":
    main()
