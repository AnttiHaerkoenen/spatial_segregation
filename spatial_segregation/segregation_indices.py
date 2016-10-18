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
    return round(np.nansum(index), 4)


def mi(p_gn):
    """
    Spatial mutual information index.
    :param p_gn: 2-dim array with groups as columns
    :return: spatial mutual information index
    """
    p_gn /= np.nansum(p_gn)
    p_g, p_n = np.broadcast_arrays(np.nansum(p_gn, axis=0, keepdims=True),
                                   np.nansum(p_gn, axis=1, keepdims=True))

    index = p_gn * np.log(p_gn / (p_g * p_n))
    return round(np.nansum(index), 4)


def calc_indices(p_gn):
    """
    Calculates Spatial forms of Karmel-MacLachlan index, Mutual information index,
    :param p_gn: 2-dim array with groups as columns, or something that can be coerced with np.asarray
    :return: dictionary of indices
    """
    try:
        p_gn = np.asarray_chkfinite(p_gn)
    except ValueError:
        raise ValueError("Incorrect input. Remove NaNs and infs.")

    index = {
        'km': km(p_gn),
        'mi': mi(p_gn)
    }

    return index
