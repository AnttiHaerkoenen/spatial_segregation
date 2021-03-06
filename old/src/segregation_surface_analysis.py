import os
import json

import pandas as pd
import numpy as np

from old.src import kde, data


class SegregationSurfaceAnalysis:
    def __init__(
            self,
            df: pd.DataFrame,
            cell_size,
            bw,
            kernel,
            alpha=1,
            convex_hull: bool =True,
            buffer=0,
            data_id=None,
            groups: tuple=("host", "other"),
    ):
        self.groups = groups
        self.data = df
        self.cell_size = cell_size
        self.kernel = kernel
        self.bw = bw
        self.alpha = alpha
        self.convex_hull = convex_hull
        self.buffer = buffer
        self.data_id = data_id

        self.surface = kde.KernelDensitySurface(
            self.data,
            cell_size=self.cell_size,
            kernel=self.kernel,
            bw=self.bw,
            a=self.alpha,
            convex_hull=self.convex_hull,
            convex_hull_buffer=self.buffer
        )
        self.surface.normalize()

        self._s = 1 - np.nansum(self.surface.min) / np.nansum(self.surface.max)

    def __str__(self):
        return(
            "Segregation Surface Analysis, S = {0}, cell size = {1}, bandwidth = {2}, kernel = {3}".format(
                self.s,
                self.cell_size,
                self.bw,
                self.kernel)
        )

    @property
    def s(self):
        return round(self._s, 3)

    # def plot(self, group, arg_dict=None):
    #     if not arg_dict:
    #         arg_dict = dict()
    #     return plt.imshow(self.surface[group], **arg_dict)
    #
    # def plot_diff(self, group_1="host", group_2="other", arg_dict=None):
    #     if not arg_dict:
    #         arg_dict = dict()
    #     return plt.imshow(self.surface[group_1] - self.surface[group_2], **arg_dict)


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
    bws = (15, 250, 25)

    d = {year: data.add_coordinates(pop_data[year], point_data, coordinates_to_meters=False)
         for year in pop_data}

    s = []

    for y, df in d.items():
        for c in cells:
            for bw in bws:
                for kern in "uniform", "biweight":
                    ana = SegregationSurfaceAnalysis(
                        df,
                        bw=bw,
                        cell_size=c,
                        kernel=kern,
                        alpha=1,
                        data_id=y
                    )
                    s.append(ana.s)
                    print(np.nansum(ana.surface['host']))

    print(s)
