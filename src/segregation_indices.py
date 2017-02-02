import numpy as np

from src.exceptions import SSValueError


def calc_indices(pop, which_indices='all', host_col=0, other_col=1, exposure_matrix=False):
    """
    Calculates spatial forms of Karmel-MacLachlan index, Mutual information index and Exposure indices.
    :param pop: 2-dim array with groups as columns, or something that can be coerced with np.asarray
    :param which_indices: which indices to calculate, default 'all' ('km', 'information', 'exposure', 'isolation')
    :param host_col: which column contains host group
    :param other_col: which column contains 'the other'
    :param exposure_matrix: whether or not to return a full exposure matrix
    :return: dictionary of indices
    """
    try:
        pop = np.asarray_chkfinite(pop)
    except ValueError:
        raise SSValueError("Incorrect input. Remove NaNs and infs.")

    if which_indices.lower() == 'all':
        which_indices = ('km', 'mi', 'exposure', 'isolation')

    index = {}

    n_areas, n_groups = pop.shape
    pop_n = pop / np.nansum(pop, axis=0, keepdims=True)
    pop_g = pop / np.nansum(pop, axis=1, keepdims=True)
    p_gn = pop / np.nansum(pop)
    p_n, p_g = np.broadcast_arrays(np.nansum(p_gn, axis=0, keepdims=True),
                                   np.nansum(p_gn, axis=1, keepdims=True))

    exposure = None

    if exposure_matrix or ('exposure' in which_indices) or ('isolation' in which_indices):
        a = pop_n.reshape((n_groups, 1, n_areas))
        b = pop_g.reshape((1, n_groups, n_areas))
        exposure = np.nansum(a * b, axis=2)

    if 'km' in which_indices:
        km = np.nansum(np.abs(p_gn / (p_g * p_n) - 1) * p_n * p_g)
        index['km'] = round(km, 3)

    if 'information' in which_indices:
        mi = np.nansum(p_gn * np.log(p_gn / (p_g * p_n)))
        index['information'] = round(mi, 3)

    if 'exposure' in which_indices:
        index['exposure'] = round(exposure[host_col, other_col], 3)

    if 'isolation' in which_indices:
        index['isolation'] = round(exposure[other_col, other_col], 3)

    if exposure_matrix:
        index['P'] = exposure

    return index
