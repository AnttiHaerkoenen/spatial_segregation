import os
import json
import datetime

import pandas as pd
import matplotlib.pyplot as plt

from spatial_segregation import segregation_index_analysis, segregation_surface_analysis, data, kde
from spatial_segregation.exceptions import AnalysesException


class Analyses:
    def __init__(self,
                 data_dict,
                 cell_sizes,
                 kernels,
                 bws,
                 alphas,
                 simulations):
        self.data_dict = data_dict
        self.cell_sizes = cell_sizes
        self.kernels = kernels
        self.bws = bws
        self.alphas = alphas
        self.simulations = simulations

        self._results = []
        self.analysis = None

    def __getitem__(self, item):
        try:
            self.results[item]
        except IndexError as ie:
            raise ie
        except TypeError as te:
            raise te

    @property
    def results(self):
        return pd.DataFrame(self._results)

    def save(self, file=None):
        if not file:
            file = "{0}_{1}".format(
                self.__class__.__name__,
                datetime.date.today()
            )

        try:
            self.results.to_csv(file)
        except IOError:
            raise AnalysesException("Error! Saving failed.")

    def load(self, file=None):
        if not file:
            file = "{0}_{1}".format(
                self.__class__.__name__,
                datetime.date.today()
            )
        try:
            self._results = pd.DataFrame.from_csv(file)
        except IOError:
            raise AnalysesException("File not found")

    def analyse(self):
        raise AnalysesException("Not implemented")

########################################################################################################################


class SegregationSurfaceAnalyses(Analyses):
    def __init__(self,
                 data_dict,
                 cell_sizes=(25,),
                 kernels=("distance_decay",),
                 bws=(1,),
                 alphas=(1,),
                 simulations=0,
                 convex_hull=True,
                 buffers=(1,)):
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
        self.analysis = segregation_surface_analysis.SegregationSurfaceAnalysis
        self.analyse()

    def analyse(self):
        for y, d in self.data_dict.items():
            for c in self.cell_sizes:
                for bw in self.bws:
                    for kern in self.kernels:
                        for b in self.buffers:
                            for a in self.alphas:
                                ana = self.analysis(
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
    def __init__(self,
                 data_dict,
                 cell_sizes=(25,),
                 kernels=("distance_decay",),
                 bws=(1,),
                 alphas=(1,),
                 simulations=0,
                 which_indices="all",
                 convex_hull=True,
                 buffers=(1,)):
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
        self.analysis = segregation_index_analysis.SegregationIndexAnalysis
        self.analyse()

    def analyse(self):
        for y, d in self.data_dict.items():
            for c in self.cell_sizes:
                for bw in self.bws:
                    for kern in self.kernels:
                        for b in self.buffers:
                            for a in self.alphas:
                                ana = self.analysis(
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

    cells = [i for i in range(20, 81, 20)]
    bandwidths = [i for i in range(50, 501, 150)]

    data = {year: data.add_coordinates(value, point_data, coordinates_to_meters=False)
            for year, value in pop_data.items()}

    ana = SegregationSurfaceAnalyses(
        data_dict=data,
        cell_sizes=cells,
        kernels=[k for k in kde.KERNELS],
        bws=bandwidths
    )
    ana.save("SegregationSurfaceAnalysis_kaikki")
    print(ana.results)

    ana2 = SegregationIndexAnalyses(
        data_dict=data,
        cell_sizes=cells,
        kernels=[k for k in kde.KERNELS],
        bws=bandwidths
    )
    ana2.save("SegregationIndexAnalysis_kaikki")
    print(ana2.results)
