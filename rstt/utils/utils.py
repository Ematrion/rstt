import numpy as np


def flatten(list):
    # https://stackoverflow.com/questions/952914/how-do-i-make-a-flat-list-out-of-a-list-of-lists
    return [item for sublist in list for item in sublist]


def uniques(values: list):
    # inspired by:
    # https://stackoverflow.com/questions/61378055/how-to-find-values-repeated-more-than-n-number-of-times-using-only-numpy
    np_val = np.array(values)
    vals, counts = np.unique(np_val, return_counts=True)
    count = dict(zip(vals, counts))
    return set([key for key, value in count.items() if value == 1])


def multiples(values: list):
    return set([value for value in values if value not in uniques(values)])


def power_of_two(n):
    # https://stackoverflow.com/questions/57025836/how-to-check-if-a-given-number-is-a-power-of-two
    return (n != 0) and (n & (n-1) == 0)


def nmax(l: list, n: int):
    # https://stackoverflow.com/questions/50477976/location-of-n-max-values-in-a-python-list
    b = l[:]
    locations = []
    minimum = min(b)-1
    for i in range(n):
        maxIndex = b.index(max(b))
        locations.append(maxIndex)
        b[maxIndex] = minimum
    return [l[loc] for loc in locations]
