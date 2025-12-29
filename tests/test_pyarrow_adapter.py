"""Tests for PyArrow adapter."""

import pytest

from wut_is.adapters import dispatch_adapter


pa = pytest.importorskip("pyarrow")


def test_pyarrow_table() -> None:
    table = pa.table({"a": [1, 2], "b": ["x", "y"]})
    meta = dispatch_adapter(table)
    assert meta["adapter_used"] == "PyArrowAdapter"
    assert meta["metadata"]["type"] == "pyarrow_table"
    assert meta["metadata"]["rows"] == 2
