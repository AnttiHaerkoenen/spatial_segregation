import segregation_index_functions as sif

all_index_functions = {
    'host_share': sif.host_share,
    'gini': sif.gini,
    'km': sif.km,
    'hpg': sif.hpg
}


class Indices:
    def __init__(self, kde_surface, index_functions="all"):
        if index_functions.lower() == "all":
            self.index_functions = all_index_functions
        else:
            self.index_functions = {k: all_index_functions[k] for k in index_functions}

        self.data = kde_surface

    def __str__(self):
        string = ['Indices:']

        for key in self.indices:
            string.append('{0:12} {1:.3f}'.format(key, self.indices[key]))

        return '\n'.join(string)

    @property
    def indices(self):
        indices = {}

        for key in self.index_functions:
            indices[key] = self.index_functions[key](self.data.host, self.data.other)

        return indices

########################################################################################################################


def main():
    pass


if __name__ == '__main__':
    main()
