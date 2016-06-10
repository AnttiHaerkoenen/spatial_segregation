import segregation_index_functions as sif

all_index_functions = {
    'host_share': sif.host_share,
    'gini': sif.gini,
    'km': sif.km,
    'hpg': sif.hpg
}


class SegregationIndices:
    def __init__(self, kde_surface, index_functions="all"):
        if index_functions.lower == "all":
            self.index_functions = all_index_functions
        else:
            self.index_functions = {}
            for key in index_functions:
                self.index_functions[key] = all_index_functions[key]

        self.data = kde_surface

    def __str__(self):
        string = ['Indices:']

        for key in self.indices:
            string.append('{0:10} \t {1}'.format(key, self.indices[key]))

        return '\n'.join(string)

    @property
    def indices(self):
        indices = {key: function(self.data) for key, function in self.index_functions}
        return indices

########################################################################################################################


def main():
    pass


if __name__ == '__main__':
    main()