import os
from functools import wraps
from time import time

import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import MultiPoint, Point
from libpysal.weights import Kernel
from segregation import spatial
from surface_based import _surface_dissim


def timing(f):
    @wraps(f)
    def wrap(*args, **kw):
        ts = time()
        result = f(*args, **kw)
        te = time()
        print(f'func: {f.__name__} time: {te - ts} sec')
        return result
    return wrap


@timing
def my_analysis(data):
    s, _ = _surface_dissim(data, function='box', bandwidth=10, group_1_pop_var='pop1', group_2_pop_var='pop2')
    return s


if __name__ == '__main__':
    os.chdir('../data')
    data_dict = {
        'geometry': [
            Point(11, 12), Point(12, 13), Point(13, 13),
            Point(11, 22), Point(12, 23), Point(13, 23),
            Point(11, 32), Point(12, 33), Point(13, 33),
            Point(11, 42), Point(12, 43), Point(13, 43),
            Point(11, 52), Point(12, 53), Point(13, 53),
        ],
        'pop1': [1, 2, 3] * 5,
        'pop2': [0, 1, 1, 2, 4] * 3,
    }
    data = gpd.GeoDataFrame.from_dict(data_dict)
    print(my_analysis(data))
