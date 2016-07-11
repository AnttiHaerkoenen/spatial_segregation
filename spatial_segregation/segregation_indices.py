import numpy as np


def km(p_gn):
    """
    Karmel-MacLachlan index of segregation.

    :param p_gn: 2-dim array with groups as columns
    :return: km index
    """
    p_g, p_n = np.broadcast_arrays(p_gn.sum(axis=0, keepdims=True),
                                   p_gn.sum(axis=1, keepdims=True))

    index = np.abs(p_gn / (p_g * p_n) - 1) * p_n * p_g
    return index.sum()


########################################################################################################################


all_index_functions = {
    'km': km
}


def calc_indices(kde_surface, index_functions='all'):
    """
    Calculates specified indices.

    :param kde_surface:
    :param index_functions:
    :return:
    """
    if index_functions.lower() == "all":
        index_functions = all_index_functions
    else:
        index_functions = {k: all_index_functions[k] for k in index_functions}

    data = np.hstack((kde_surface.host, kde_surface.other))
    data /= data.sum()

    indices = dict()

    for key in index_functions:
        indices[key] = index_functions[key](data)

    return indices
