import numpy as np

import segregation_index_functions as sif


all_index_functions = {
    'host_share': sif.host_share,
    'km': sif.km,
    'hpg': sif.hpg
}


def calc_indices(kde_surface, index_functions='all'):
        if index_functions.lower() == "all":
            index_functions = all_index_functions
        else:
            index_functions = {k: all_index_functions[k] for k in index_functions}

        data = np.stack((kde_surface.host.ravel(), kde_surface.other.ravel()), axis=-1)

        indices = dict()

        for key in index_functions:
            indices[key] = index_functions[key](data)

        return indices

########################################################################################################################


def main():
    pass


if __name__ == '__main__':
    main()
