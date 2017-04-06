import matplotlib.pyplot as plt

from src import plotting, kernel_functions as kf

plt.style.use('classic')

for k, f in kf.KERNELS.items():
    scale = 2 if k == 'gaussian' else 1
    plotting.plot_kernel(f, 1)
    plt.ylim((-0.2, 1.2))
    plt.show()
