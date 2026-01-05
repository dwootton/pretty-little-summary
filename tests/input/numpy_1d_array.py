ID = "numpy_1d_array"
TITLE = "NumPy 1D array"
TAGS = ["numpy", "array"]
REQUIRES = ['numpy']
DISPLAY_INPUT = "np.arange(10, dtype=np.int64)"
EXPECTED = "A numpy array with shape (10,) and dtype int64. Sample: [0, 1, 2, 3, 4 ... 5, 6, 7, 8, 9]."


def build():
    import numpy as np

    return np.arange(10, dtype=np.int64)
