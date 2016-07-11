import os

import pysal
import pandas as pd

import data

DATA_FILE = 'data'


class SegregationAnalysis:
    def __init__(self, data_frame, cell_size, kernel, bw, alpha=1):
        self.data = data_frame
        self.cell_size = cell_size
        self.kernel = kernel
        self.bw = bw
        self.alpha = alpha
        self.simulations = None

    def simulate(self, rep=1000):
        self.simulations = []

        for _ in range(rep):
            # TODO
            pass

    @property
    def simulated(self):
        return pd.DataFrame.from_dict(self.simulations)

########################################################################################################################


def main():
    os.chdir(DATA_FILE)
    v80 = data.aggregate_sum(data.reform(pd.read_csv('1880.csv', sep='\t')))
    v00 = data.aggregate_sum(data.reform(pd.read_csv('1900.csv', sep='\t')))
    v20 = data.aggregate_sum(data.reform(pd.read_csv('1920.csv', sep='\t')))

    pop_data = {
        1880: v80,
        1900: v00,
        1920: v20
    }

    point_shp = pysal.open("points.shp")
    point_db = pysal.open("points.dbf", 'r')

    point_data = []
    for i in range(len(point_shp)):
        point_data.append([point_db[i][0][1], point_shp[i][0], point_shp[i][1]])

    cells = [i for i in range(15, 61, 15)]
    bws = [i for i in range(2, 6)]

    data = data.add_coordinates(pop_data[1880], point_data)



if __name__ == "__main__":
    main()
