from spatial_segregation import kde, kernel_functions, data


class SegregationSurfaceAnalysis:
    def __init__(self,
                 data_dict,
                 cell_size,
                 bw,
                 kernel,
                 which_indices='all',
                 alpha=1,
                 convex_hull=True,
                 buffer=0,
                 data_id=None):
        self.data = data_dict
        self.cell_size = cell_size
        self.kernel = kernel
        self.bw = round(bw * cell_size)
        self.alpha = alpha
        self.convex_hull=convex_hull
        self.buffer = buffer
        self.which_indices = which_indices
        self.data_id = data_id

        self.surface = kde.KernelDensitySurface(
            self.data,
            self.cell_size,
            self.kernel,
            self.bw,
            self.alpha,
            self.convex_hull,
            self.buffer
        )

    def __str__(self):
        pass


########################################################################################################################


def main():
    pass


if __name__ == '__main__':
    main()
