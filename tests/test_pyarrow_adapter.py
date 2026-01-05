"""Tests for PyArrow adapter."""

import pytest

from pretty_little_summary.adapters import dispatch_adapter
from pretty_little_summary.synthesizer import deterministic_summary
from tests.input import build_input, expected_output, load_example


pa = pytest.importorskip("pyarrow")


def test_pyarrow_table() -> None:
    example = load_example("pyarrow_table")
    meta = dispatch_adapter(build_input(example))
    assert meta["adapter_used"] == "PyArrowAdapter"
    assert meta["metadata"]["type"] == "pyarrow_table"
    assert meta["metadata"]["rows"] == 2
    summary = deterministic_summary(meta)
    print("pyarrow:", summary)
    assert summary == expected_output(example, meta)
