ID = "numpy_2d_array"
TITLE = "NumPy 2D array"
TAGS = ["numpy", "array"]
REQUIRES = ['numpy']
DISPLAY_INPUT = "np.arange(12, dtype=np.float64).reshape(3, 4)"
EXPECTED = (
    "A numpy array with shape (3, 4) and dtype float64. Sample corner: "
    "[[0.0, 1.0, 2.0], [4.0, 5.0, 6.0], [8.0, 9.0, 10.0]]. "
    "Stats: range 0 to 11, mean 5.5, std 3.6."
)


def build():
    import numpy as np

    return np.arange(12, dtype=np.float64).reshape(3, 4)
