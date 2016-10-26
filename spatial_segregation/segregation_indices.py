import numpy as np


def calc_indices(pop, indices='all', host_col=0, other_col=1, exposure_matrix=False):
    """
    Calculates spatial forms of Karmel-MacLachlan index, Mutual information index and Exposure indices.
    :param pop: 2-dim array with groups as columns, or something that can be coerced with np.asarray
    :param indices: which indices to calculate, default 'all' ('km', 'mi', 'exposure', 'isolation')
    :param host_col: which column contains host group
    :param other_col: which column contains 'the other'
    :param exposure_matrix: whether or not to return a full exposure matrix
    :return: dictionary of indices
    """
    try:
        pop = np.asarray_chkfinite(pop)
    except ValueError:
        raise ValueError("Incorrect input. Remove NaNs and infs.")

    if indices.lower() == 'all':
        indices = ('km', 'mi', 'exposure', 'isolation')

    index = {}

    n_areas, n_groups = pop.shape
    pop_n = pop / np.nansum(pop, axis=0, keepdims=True)
    pop_g = pop / np.nansum(pop, axis=1, keepdims=True)
    p_gn = pop / np.nansum(pop)
    p_n, p_g = np.broadcast_arrays(np.nansum(p_gn, axis=0, keepdims=True),
                                   np.nansum(p_gn, axis=1, keepdims=True))

    exposure = None

    if exposure_matrix or ('exposure' in indices) or ('isolation' in indices):
        a = pop_n.reshape((n_groups, 1, n_areas))
        b = pop_g.reshape((1, n_groups, n_areas))
        exposure = np.nansum(a * b, axis=2)

    if 'km' in indices:
        km = np.nansum(np.abs(p_gn / (p_g * p_n) - 1) * p_n * p_g)
        index['km'] = round(km, 4)

    if 'mi' in indices:
        mi = np.nansum(p_gn * np.log(p_gn / (p_g * p_n)))
        index['mi'] = round(mi, 4)

    if 'exposure' in indices:
        index['exposure'] = exposure[host_col, other_col]

    if 'isolation' in indices:
        index['isolation'] = exposure[other_col, other_col]

    if exposure_matrix:
        index['P'] = exposure

    return index