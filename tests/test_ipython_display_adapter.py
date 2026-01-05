"""Tests for IPython display adapter."""

import pytest

from pretty_little_summary.adapters import dispatch_adapter
from pretty_little_summary.synthesizer import deterministic_summary
from tests.input import build_input, expected_output, load_example


ipython = pytest.importorskip("IPython")


def test_ipython_display_adapter() -> None:
    example = load_example("ipython_display_adapter")
    meta = dispatch_adapter(build_input(example))
    assert meta["adapter_used"] == "IPythonDisplayAdapter"
    assert meta["metadata"]["type"] == "ipython_display"
    summary = deterministic_summary(meta)
    print("ipython_display:", summary)
    assert summary == expected_output(example, meta)
