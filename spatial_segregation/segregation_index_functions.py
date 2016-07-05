import numpy as np




########################################################################################################################


def main():
    x = np.random.rand(20, 3)
    print(x)
    print("host share: ", host_share(x))
    print("km: ", km(x))
    print("hpg: ", hpg(x))


if __name__ == '__main__':
    main()
