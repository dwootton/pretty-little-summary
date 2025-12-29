"""Tests for PyArrow adapter."""

import pytest

from pretty_little_summary.adapters import dispatch_adapter
from pretty_little_summary.synthesizer import deterministic_summary


pa = pytest.importorskip("pyarrow")


def test_pyarrow_table() -> None:
    table = pa.table({"a": [1, 2], "b": ["x", "y"]})
    meta = dispatch_adapter(table)
    assert meta["adapter_used"] == "PyArrowAdapter"
    assert meta["metadata"]["type"] == "pyarrow_table"
    assert meta["metadata"]["rows"] == 2
    summary = deterministic_summary(meta)
    print("pyarrow:", summary)
    parts = [
        f"A PyArrow Table with {meta['metadata']['rows']} rows and {meta['metadata']['columns']} columns."
    ]
    schema = meta["metadata"].get("schema") or {}
    if schema:
        cols = []
        for name, dtype in list(schema.items())[:3]:
            cols.append(f"{name} ({dtype})")
        if cols:
            parts.append(f"Schema: {', '.join(cols)}.")
    memory = meta["metadata"].get("memory")
    if memory:
        parts.append(f"Memory: {memory}.")
    sample_rows = meta["metadata"].get("sample_rows")
    if sample_rows:
        parts.append(f"Sample row: {sample_rows[0]}.")
    elif meta["metadata"].get("sample_rows_omitted"):
        parts.append("Sample rows omitted for size/perf.")
    assert summary == " ".join(parts)
