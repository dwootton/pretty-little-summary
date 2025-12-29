"""Tests for NumPy adapter."""

import pytest

from pretty_little_summary.adapters import dispatch_adapter
from pretty_little_summary.synthesizer import deterministic_summary


np = pytest.importorskip("numpy")


def test_numpy_1d_array() -> None:
    arr = np.arange(10, dtype=np.int64)
    meta = dispatch_adapter(arr)
    assert meta["adapter_used"] == "NumpyAdapter"
    assert meta["metadata"]["type"] == "ndarray"
    summary = deterministic_summary(meta)
    print("numpy_1d:", summary)
    assert summary == (
        "A numpy array with shape (10,) and dtype int64. "
        "Sample: [0, 1, 2, 3, 4 ... 5, 6, 7, 8, 9]."
    )


def test_numpy_2d_array() -> None:
    arr = np.arange(12, dtype=np.float64).reshape(3, 4)
    meta = dispatch_adapter(arr)
    assert meta["metadata"]["ndim"] == 2
    summary = deterministic_summary(meta)
    print("numpy_2d:", summary)
    assert summary == (
        "A numpy array with shape (3, 4) and dtype float64. "
        "Sample corner: [[0.0, 1.0, 2.0], [4.0, 5.0, 6.0], [8.0, 9.0, 10.0]]."
    )


def test_numpy_scalar() -> None:
    scalar = np.float64(3.14)
    meta = dispatch_adapter(scalar)
    assert meta["metadata"]["type"] == "numpy_scalar"
    summary = deterministic_summary(meta)
    print("numpy_scalar:", summary)
    assert summary == "A numpy float64 scalar with value 3.14."
