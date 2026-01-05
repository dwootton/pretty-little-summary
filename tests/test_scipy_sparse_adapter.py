"""Tests for scipy sparse adapter."""

import pytest

from pretty_little_summary.adapters import dispatch_adapter
from pretty_little_summary.synthesizer import deterministic_summary
from tests.input import build_input, expected_output, load_example


sp = pytest.importorskip("scipy.sparse")


def test_scipy_sparse_csr() -> None:
    example = load_example("scipy_sparse_csr")
    meta = dispatch_adapter(build_input(example))
    assert meta["adapter_used"] == "ScipySparseAdapter"
    assert meta["metadata"]["type"] == "sparse_matrix"
    assert meta["metadata"]["nnz"] == 2
    summary = deterministic_summary(meta)
    print("scipy_sparse:", summary)
    assert summary == expected_output(example, meta)
