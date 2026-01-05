"""Tests for attrs adapter."""

import pytest

from pretty_little_summary.adapters import dispatch_adapter
from pretty_little_summary.synthesizer import deterministic_summary
from tests.input import build_input, expected_output, load_example


attr = pytest.importorskip("attr")


def test_attrs_adapter() -> None:
    example = load_example("attrs_adapter")
    meta = dispatch_adapter(build_input(example))
    assert meta["adapter_used"] == "AttrsAdapter"
    assert meta["metadata"]["type"] == "attrs"
    summary = deterministic_summary(meta)
    print("attrs:", summary)
    assert summary == expected_output(example, meta)
