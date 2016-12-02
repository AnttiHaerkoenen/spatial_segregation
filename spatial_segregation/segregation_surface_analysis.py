import os
import json

import matplotlib.pyplot as plt
import pandas as pd

from spatial_segregation import kde, data, util


class SegregationSurfaceAnalysis:
    def __init__(self,
                 df,
                 cell_size,
                 bw,
                 kernel,
                 alpha=1,
                 convex_hull=True,
                 buffer=0,
                 data_id=None,
                 groups=("host", "other")):
        self.groups = groups
        self.data = util.normalise(df, columns=self.groups)
        self.cell_size = cell_size
        self.kernel = kernel
        self.bw = round(bw * cell_size)
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

        self.s = 1 - sum(self.surface.min) / sum(self.surface.max)

    def __str__(self):
        return(
            "Segregation Surface Analysis, S = {0}, cell size = {1}, bw = {2}, kernel = {3}".format(
                self.s,
                self.cell_size,
                self.bw,
                self.kernel)
        )

    def plot(self, group, style="classic"):
        plt.style.use(style)
        plt.imshow(self.surface[group])
        plt.show()


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

    for y, df in d.items():
        for c in cells:
            for bw in bws:
                for kern in "uniform", "distance_decay":
                    ana = SegregationSurfaceAnalysis(
                        df,
                        bw=bw,
                        cell_size=c,
                        kernel=kern,
                        alpha=1,
                        data_id=y
                    )
                    ana.plot("host")
