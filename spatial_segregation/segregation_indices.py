import numpy as np


def km(p_gn):
    """
    Karmel-MacLachlan index of segregation.
    :param p_gn: 2-dim array with groups as columns
    :return: km index
    """
    p_gn /= np.nansum(p_gn)
    p_g, p_n = np.broadcast_arrays(np.nansum(p_gn, axis=0, keepdims=True),
                                   np.nansum(p_gn, axis=1, keepdims=True))

    index = np.abs(p_gn / (p_g * p_n) - 1) * p_n * p_g
    sum_ = np.nansum(index)

    if sum_ < 0:
        return 0
    elif sum_ > 1:
        return 1
    else:
        return sum_


def calc_indices(p_gn):
    index = dict()

    index['km'] = km(p_gn)

    return index
