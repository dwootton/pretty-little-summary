"""Tests for scipy sparse adapter."""

import pytest

from wut_is.adapters import dispatch_adapter
from wut_is.synthesizer import deterministic_summary


sp = pytest.importorskip("scipy.sparse")


def test_scipy_sparse_csr() -> None:
    matrix = sp.csr_matrix([[0, 1], [2, 0]])
    meta = dispatch_adapter(matrix)
    assert meta["adapter_used"] == "ScipySparseAdapter"
    assert meta["metadata"]["type"] == "sparse_matrix"
    assert meta["metadata"]["nnz"] == 2
    print("scipy_sparse:", deterministic_summary(meta))
    assert "sparse matrix" in deterministic_summary(meta)
