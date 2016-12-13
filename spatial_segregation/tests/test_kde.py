import numpy as np
import numpy.testing as npt
import pandas as pd
import pandas.util.testing as pdt

from spatial_segregation import kde

data1 = pd.DataFrame(np.random.randint(0, 1000, (20, 4)), columns='x y host other'.split())

data2 = pd.DataFrame({'x': [-100, 100, 100, -100],
                      'y': [100, 100, -100, -100],
                      'host': [2, 2, 2, 2],
                      'other': [0, 0, 0, 1]})

data3 = {'x': np.array((0, 1, 1)),
         'y': np.array((0, 1, 1))}

data4 = {'x': np.array((-1, 1, 1, -1)),
         'y': np.array((1, 1, -1, -1))}

data5 = {'x': np.array((-2, 2, 2, -2)),
         'y': np.array((1, 1, -1, -1))}

data6 = {'x': np.array((-0.5, 0.5, 0.5, -0.5)),
         'y': np.array((0.5, 0.5, -0.5, -0.5))}

data_ones = pd.DataFrame(np.ones((2, 4)), columns='x y host other'.split())

data_empty = {'x': np.array(()),
              'y': np.array(())}
