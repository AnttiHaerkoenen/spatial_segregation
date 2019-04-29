import datetime

import pandas as pd

from src import segregation_index_analysis, segregation_surface_analysis, data, kde, plotting


class Analyses:
    _analysis = None

    def __init__(
            self,
            data_dict,
            parameters,
            simulations
    ):
        self.data_dict = data_dict
        self.parameters = parameters
        self.simulations = simulations

        self._results = []

    def __getitem__(self, item):
        return self.results[item]

    @property
    def results(self):
        return pd.DataFrame(self._results)

    def save(self, file=None):
        if not file:
            file = "{0}_{1}.csv".format(
                self.__class__.__name__,
                datetime.date.today()
            )

        self.results.to_csv(file)

    def load(self, file=None):
        if not file:
            file = "{0}_{1}.csv".format(
                self.__class__.__name__,
                datetime.date.today()
            )
        self._results = pd.DataFrame.from_csv(file)

    def analyse(self):
        raise NotImplementedError

########################################################################################################################


class SegregationSurfaceAnalyses(Analyses):
    def __init__(
            self,
            data_dict,
            parameters,
            simulations=0,
            convex_hull=True,
            buffers=(1,),
    ):
        super(SegregationSurfaceAnalyses, self).__init__(
            data_dict=data_dict,
            parameters=parameters,
            simulations=simulations,
        )
        self.convex_hull = convex_hull
        self.buffers = buffers
        self._analysis = segregation_surface_analysis.SegregationSurfaceAnalysis

    def analyse(self):
        for y, d in self.data_dict.items():
            for par in self.parameters:
                for b in self.buffers:
                    ana = self._analysis(
                        d,
                        cell_size=par.cell_size,
                        bw=par.bw,
                        kernel=par.kernel,
                        alpha=par.alpha,
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
            data_dict,
            parameters,
            simulations=0,
            which_indices="all",
            convex_hull=True,
            buffers=(1,)
    ):
        super(SegregationIndexAnalyses, self).__init__(
            data_dict=data_dict,
            parameters=parameters,
            simulations=simulations
        )
        self.which_indices = which_indices
        self.convex_hull = convex_hull
        self.buffers = buffers
        self._analysis = segregation_index_analysis.SegregationIndexAnalysis

    def analyse(self):
        for y, d in self.data_dict.items():
            for par in self.parameters:
                for b in self.buffers:
                    ana = self._analysis(
                        d,
                        cell_size=par.cell_size,
                        bw=par.bw,
                        kernel=par.kernel,
                        alpha=par.alpha,
                        which_indices=self.which_indices,
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
