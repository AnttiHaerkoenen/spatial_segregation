import os
import json
import datetime

import pandas as pd
import matplotlib.pyplot as plt

from spatial_segregation import segregation_index_analysis, segregation_surface_analysis, data


class Analyses:
    def __init__(self,
                 analysis,
                 data_frame,
                 cell_sizes=(25,),
                 kernels=("distance_decay",),
                 bws=(1,),
                 alphas=(1,),
                 simulations=0):
        self.analysis = analysis
        self.data = data_frame

        self.cell_sizes = cell_sizes

        self.kernels = kernels
        self.bws = bws
        self.alphas = alphas

        self.simulations = simulations

        self._results = None
        self.analyse()

    def __getitem__(self, item):
        try:
            self.results[item]
        except IndexError as ie:
            print("IndexError!")
            raise ie
        except TypeError as te:
            print("Key is of wrong type!")
            raise te
        except Exception as e:
            print("Something went wrong")
            raise e

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
            print("Error! Saving failed.")

    def load(self, file=None):
        if not file:
            file = "{0}_{1}".format(
                self.__class__.__name__,
                datetime.date.today()
            )

        try:
            self._results = pd.DataFrame.from_csv(file)
        except IOError:
            print("File not found")

    def analyse(self):
        print("Placeholder method!")

########################################################################################################################


class SegregationSurfaceAnalyses(Analyses):
    def __init__(self,
                 data_frame,
                 cell_sizes=(25,),
                 kernels=("distance_decay",),
                 bws=(1,),
                 alphas=(1,),
                 simulations=0,
                 convex_hull=True,
                 buffers=(1,)):
        Analyses.__init__(
            self,
            segregation_surface_analysis.SegregationSurfaceAnalysis,
            data_frame,
            cell_sizes=cell_sizes,
            kernels=kernels,
            bws=bws,
            alphas=alphas,
            simulations=simulations
        )
        self.convex_hull = convex_hull
        self.buffers = buffers

    def analyse(self):
        for y, d in self.data.items():
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
                                        **ana.param
                                    }
                                )

    def plot(self, x="year", arg_dict=None):
        if not arg_dict:
            arg_dict = dict()
        # TODO
        pass

########################################################################################################################


class SegregationIndexAnalyses(Analyses):
    def __init__(self,
                 data_frame,
                 cell_sizes=(25,),
                 kernels=("distance_decay",),
                 bws=(1,),
                 alphas=(1,),
                 simulations=0,
                 which_indices="all",
                 convex_hull=True,
                 buffers=(1,)):
        Analyses.__init__(
            self,
            segregation_index_analysis.SegregationIndexAnalysis,
            data_frame,
            cell_sizes=cell_sizes,
            kernels=kernels,
            bws=bws,
            alphas=alphas,
            simulations=simulations
        )
        self.which_indices = which_indices
        self.convex_hull = convex_hull
        self.buffers = buffers

    def analyse(self):
        for y, d in self.data.items():
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
                                ana.simulate(self.simulations)
                                self._results.append({
                                    "year": y,
                                    **ana.param,
                                    **ana.indices,
                                    **ana.p
                                })

    def plot(self):
        pass

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
    bandwidths = (1.5, 2, 2.5)

    d = {year: data.add_coordinates(pop_data[year], point_data, coordinates_to_meters=False)
         for year in pop_data}
