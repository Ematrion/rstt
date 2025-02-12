import numpy as np


def uniques(values: list):
    # inspired by:
    # https://stackoverflow.com/questions/61378055/how-to-find-values-repeated-more-than-n-number-of-times-using-only-numpy
    np_val = np.array(values)
    vals, counts = np.unique(np_val, return_counts=True)
    count = dict(zip(vals, counts))
    return set([key for key, value in count.items() if value == 1])

def multiples(values: list):
    return set([value for value in values if value not in uniques(values)])