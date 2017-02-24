import os
import json
import datetime

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from src import segregation_index_analysis, segregation_surface_analysis, data, kde, plotting
from src.exceptions import SSIndexError, SSTypeError, SSIOError, SSNotImplementedError


class Analyses:
    _analysis = None

    def __init__(
            self,
            data_dict,
            cell_sizes,
            kernels,
            bws,
            alphas,
            simulations
    ):
        self.data_dict = data_dict
        self.cell_sizes = cell_sizes
        self.kernels = kernels
        self.bws = bws
        self.alphas = alphas
        self.simulations = simulations

        self._results = []

    def __getitem__(self, item):
        try:
            self.results[item]
        except IndexError:
            raise SSIndexError
        except TypeError:
            raise SSTypeError

    @property
    def results(self):
        return pd.DataFrame(self._results)

    def save(self, file=None):
        if not file:
            file = "{0}_{1}.csv".format(
                self.__class__.__name__,
                datetime.date.today()
            )

        try:
            self.results.to_csv(file)
        except IOError:
            raise SSIOError("Error! Saving failed.")

    def load(self, file=None):
        if not file:
            file = "{0}_{1}.csv".format(
                self.__class__.__name__,
                datetime.date.today()
            )
        try:
            self._results = pd.DataFrame.from_csv(file)
        except IOError:
            raise SSIOError("File not found")

    def analyse(self):
        raise SSNotImplementedError

########################################################################################################################


class SegregationSurfaceAnalyses(Analyses):
    def __init__(
            self,
            data_dict=None,
            cell_sizes=(25,),
            kernels=("biweight",),
            bws=(1,),
            alphas=(1,),
            simulations=0,
            convex_hull=True,
            buffers=(1,)
    ):
        super().__init__(
            data_dict=data_dict,
            cell_sizes=cell_sizes,
            kernels=kernels,
            bws=bws,
            alphas=alphas,
            simulations=simulations
        )
        self.convex_hull = convex_hull
        self.buffers = buffers
        self._analysis = segregation_surface_analysis.SegregationSurfaceAnalysis

    def analyse(self):
        for y, d in self.data_dict.items():
            for c in self.cell_sizes:
                for bw in self.bws:
                    for kern in self.kernels:
                        for b in self.buffers:
                            for a in self.alphas:
                                ana = self._analysis(
                                    d,
                                    cell_size=c,
                                    bw=bw,
                                    kernel=kern,
                                    alpha=a,
                                    buffer=b,
                                    convex_hull=self.convex_hull,
                                    data_id=y
                                )
                                self._results.append(
                                    {
                                        "year": y,
                                        "s": ana.s,
                                        **ana.surface.param
                                    }
                                )


########################################################################################################################


class SegregationIndexAnalyses(Analyses):
    def __init__(
            self,
            data_dict=None,
            cell_sizes=(25,),
            kernels=("biweight",),
            bws=(1,),
            alphas=(1,),
            simulations=0,
            which_indices="all",
            convex_hull=True,
            buffers=(1,)
    ):
        super().__init__(
            data_dict=data_dict,
            cell_sizes=cell_sizes,
            kernels=kernels,
            bws=bws,
            alphas=alphas,
            simulations=simulations
        )
        self.which_indices = which_indices
        self.convex_hull = convex_hull
        self.buffers = buffers
        self._analysis = segregation_index_analysis.SegregationIndexAnalysis

    def analyse(self):
        for y, d in self.data_dict.items():
            for c in self.cell_sizes:
                for bw in self.bws:
                    for kern in self.kernels:
                        for b in self.buffers:
                            for a in self.alphas:
                                ana = self._analysis(
                                        d,
                                        cell_size=c,
                                        bw=bw,
                                        kernel=kern,
                                        which_indices=self.which_indices,
                                        alpha=a,
                                        buffer=b,
                                        convex_hull=self.convex_hull,
                                        data_id=y
                                )
                                if self.simulations:
                                    ana.simulate(self.simulations)
                                self._results.append({
                                    "year": y,
                                    **ana.surface.param,
                                    **ana.indices,
                                    **ana.p
                                })

########################################################################################################################


if __name__ == '__main__':
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))
    os.chdir(os.path.join(os.path.abspath(os.path.pardir), data.DATA_DIR))

    v80 = data.aggregate_sum(data.reform(pd.read_csv('1880.csv')))
    v00 = data.aggregate_sum(data.reform(pd.read_csv('1900.csv')))
    v20 = data.aggregate_sum(data.reform(pd.read_csv('1920.csv')))

    pop_data = {
        '1880': v80,
        '1900': v00,
        '1920': v20
    }

    with open('points1878.geojson') as f:
        point_data = json.load(f)

    cells = 25, 50, 75
    bandwidths = 25, 50, 100, 150, 250

    data = {year: data.add_coordinates(value, point_data, coordinates_to_meters=False)
            for year, value in pop_data.items()}

    plotting.plot_densities_all(
        data,
        cell_size=25,
        bw=100,
        kernel='biweight',
        subplot_title_param=dict(year='vuosi'),
        labels='luterilaiset ortodoksit erotus'.split(),
        title='Tiheys'
    ).set_facecolor('white')
    plt.show()

    # ana1 = SegregationSurfaceAnalyses(
    #     data_dict=data,
    #     cell_sizes=cells,
    #     kernels=[k for k in kde.KERNELS],
    #     bws=bandwidths
    # )
    # ana1.analyse()
    # ana1.save("SegregationSurfaceAnalysis_kaikki.csv")
    #
    # ana2 = SegregationIndexAnalyses(
    #     data_dict=data,
    #     cell_sizes=cells,
    #     kernels=[k for k in kde.KERNELS],
    #     bws=bandwidths
    # )
    # ana2.analyse()
    # ana2.save("SegregationIndexAnalysis_kaikki.csv")
    #
    # results = pd.merge(ana1.results, ana2.results)["year kernel bw cell_size s exposure isolation km".split()]
    # results = results.sort_values(by='year')
    # results.index = np.arange(1, len(results) + 1)
    # print(results)
    # results.to_csv("kaikki.csv")
