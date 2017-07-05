import datetime
from collections import namedtuple

import pandas as pd

from src import segregation_index_analysis, segregation_surface_analysis, data, kde, plotting
from src.exceptions import SSIndexError, SSTypeError, SSIOError, SSNotImplementedError

ParameterPermutation = namedtuple('ParameterPermutation', 'cell_size, kernel, bw, alpha')


class Parameters:
    def __init__(self):
        pass

    def __str__(self):
        pass

    def __iter__(self):
        pass


########################################################################################################################


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
        super(SegregationSurfaceAnalyses, self).__init__(
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
        super(SegregationIndexAnalyses, self).__init__(
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
    pass
