"""Tests for scipy sparse adapter."""

import pytest

from pretty_little_summary.adapters import dispatch_adapter
from pretty_little_summary.synthesizer import deterministic_summary


sp = pytest.importorskip("scipy.sparse")


def test_scipy_sparse_csr() -> None:
    matrix = sp.csr_matrix([[0, 1], [2, 0]])
    meta = dispatch_adapter(matrix)
    assert meta["adapter_used"] == "ScipySparseAdapter"
    assert meta["metadata"]["type"] == "sparse_matrix"
    assert meta["metadata"]["nnz"] == 2
    summary = deterministic_summary(meta)
    print("scipy_sparse:", summary)
    assert summary == "A csr sparse matrix with shape (2, 2)."
