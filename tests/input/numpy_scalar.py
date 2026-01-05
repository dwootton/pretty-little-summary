ID = "numpy_scalar"
TITLE = "NumPy scalar"
TAGS = ["numpy", "scalar"]
REQUIRES = ['numpy']
DISPLAY_INPUT = "np.float64(3.14)"
EXPECTED = "A numpy float64 scalar with value 3.14."


def build():
    import numpy as np

    return np.float64(3.14)
