import numpy as np


def km(p_gn):
    """
    Karmel-MacLachlan index of segregation.

    :param p_gn: 2-dim array with groups as columns
    :return: km index
    """
    p_gn /= p_gn.sum()
    p_g, p_n = np.broadcast_arrays(p_gn.sum(axis=0, keepdims=True),
                                   p_gn.sum(axis=1, keepdims=True))

    index = np.abs(p_gn / (p_g * p_n) - 1) * p_n * p_g
    return index.sum()


def calc_indices(p_gn):
    index = dict()

    index['km'] = km(p_gn)

    return index
