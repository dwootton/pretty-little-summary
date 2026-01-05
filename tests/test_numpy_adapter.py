"""Tests for NumPy adapter."""

import pytest

from pretty_little_summary.adapters import dispatch_adapter
from pretty_little_summary.synthesizer import deterministic_summary
from tests.input import build_input, expected_output, load_example


np = pytest.importorskip("numpy")


def test_numpy_1d_array() -> None:
    example = load_example("numpy_1d_array")
    meta = dispatch_adapter(build_input(example))
    assert meta["adapter_used"] == "NumpyAdapter"
    assert meta["metadata"]["type"] == "ndarray"
    summary = deterministic_summary(meta)
    print("numpy_1d:", summary)
    assert summary == expected_output(example, meta)


def test_numpy_2d_array() -> None:
    example = load_example("numpy_2d_array")
    meta = dispatch_adapter(build_input(example))
    assert meta["metadata"]["ndim"] == 2
    summary = deterministic_summary(meta)
    print("numpy_2d:", summary)
    assert summary == expected_output(example, meta)


def test_numpy_scalar() -> None:
    example = load_example("numpy_scalar")
    meta = dispatch_adapter(build_input(example))
    assert meta["metadata"]["type"] == "numpy_scalar"
    summary = deterministic_summary(meta)
    print("numpy_scalar:", summary)
    assert summary == expected_output(example, meta)
