"""Tests for NumPy adapter."""

import pytest

from wut_is.adapters import dispatch_adapter
from wut_is.synthesizer import deterministic_summary


np = pytest.importorskip("numpy")


def test_numpy_1d_array() -> None:
    arr = np.arange(10, dtype=np.int64)
    meta = dispatch_adapter(arr)
    assert meta["adapter_used"] == "NumpyAdapter"
    assert meta["metadata"]["type"] == "ndarray"
    summary = deterministic_summary(meta)
    assert "Shape:" in summary


def test_numpy_2d_array() -> None:
    arr = np.arange(12, dtype=np.float64).reshape(3, 4)
    meta = dispatch_adapter(arr)
    assert meta["metadata"]["ndim"] == 2


def test_numpy_scalar() -> None:
    scalar = np.float64(3.14)
    meta = dispatch_adapter(scalar)
    assert meta["metadata"]["type"] == "numpy_scalar"
