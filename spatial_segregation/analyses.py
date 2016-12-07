import os
import json
import datetime

import pandas as pd
import matplotlib.pyplot as plt

from spatial_segregation import kde, data, segregation_indices, util


class Analyses:
    def __init__(self,
                 data_frame,
                 cell_sizes=(25,),
                 kernels=("distance_decay",),
                 bws=(1,),
                 alphas=(1,)):
        self.data = data_frame
        self.cell_sizes = cell_sizes
        self.kernels = kernels
        self.bws = bws
        self.alphas = alphas


class SegregationSurfaceAnalyses(Analyses):
    def __init__(self,
                 data_frame):
        Analyses.__init__(self,
                          data_frame)


class SegregationIndexAnalyses(Analyses):
    def __init__(self,
                 data_frame):
        Analyses.__init__(self,
                          data_frame)


# class SegregationIndexAnalyses:
#     def __init__(self,
#                  data_frame,
#                  cell_sizes=(50,),
#                  bws=(2,),
#                  kernels=('distance_decay',),
#                  which_indices='all',
#                  buffers=None,
#                  alphas=(1,),
#                  convex_hull=True,
#                  simulations=0):
#         self.data_frame = data_frame
#         self.cell_sizes = cell_sizes
#         self.bws = bws
#         self.kernels = kernels
#         self.which_indices = which_indices
#         self.alphas = alphas
#         self.convex_hull = convex_hull
#         self.simulations = simulations
#
#         if buffers:
#             self.buffers = buffers
#         else:
#             self.buffers = self.bws[0],
#
#         self._results = []
#
#         for y, d in self.data_frame.items():
#             for c in self.cell_sizes:
#                 for bw in self.bws:
#                     for kern in self.kernels:
#                         for b in self.buffers:
#                             for a in self.alphas:
#                                 ana = SegregationIndexAnalysis(
#                                         d,
#                                         cell_size=c,
#                                         bw=bw,
#                                         kernel=kern,
#                                         which_indices=self.which_indices,
#                                         alpha=a,
#                                         buffer=b,
#                                         convex_hull=self.convex_hull,
#                                         data_id=y
#                                 )
#                                 ana.simulate(self.simulations)
#                                 self._results.append({
#                                     "year": y,
#                                     **ana.param,
#                                     **ana.indices,
#                                     **ana.p
#                                 })
#
#     def __str__(self):
#         pass
#
#     def __getitem__(self, item):
#         try:
#             self.results[item]
#         except IndexError as e:
#             print("IndexError!")
#             raise e
#         except TypeError as e:
#             print("Key is of wrong type!")
#             raise e
#
#     @property
#     def results(self):
#         return pd.DataFrame(self._results)
#
#     def plot(self):
#         pass
#
#     def save(self, file=None):
#         if not file:
#             file = "SegAnalysis_{0}".format(datetime.date.today())
#         try:
#             self.results.to_csv(file)
#         except IOError:
#             print("Error! Saving failed.")
#
#     def load(self, file=None):
#         if not file:
#             file = "SegAnalysis_{0}".format(datetime.datetime.today())
#         try:
#             self._results = pd.DataFrame.from_csv(file)
#         except IOError:
#             print("File not found")