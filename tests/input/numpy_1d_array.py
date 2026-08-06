ID = "numpy_1d_array"
TITLE = "NumPy 1D array"
TAGS = ["numpy", "array"]
REQUIRES = ['numpy']
DISPLAY_INPUT = "np.round(np.linspace(60, 95, 24), 1)  # test scores"
EXPECTED = (
    "A numpy array with shape (24,) and dtype float64. Sample: [60.0, 61.5, "
    "63.0, 64.6, 66.1 ... 88.9, 90.4, 92.0, 93.5, 95.0]. "
    "Stats: range 60 to 95, mean 78, std 11."
)


def build():
    import numpy as np

    return np.round(np.linspace(60, 95, 24), 1)
