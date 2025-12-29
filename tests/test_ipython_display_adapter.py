"""Tests for IPython display adapter."""

import pytest

from pretty_little_summary.adapters import dispatch_adapter
from pretty_little_summary.synthesizer import deterministic_summary


ipython = pytest.importorskip("IPython")
from IPython.display import HTML  # noqa: E402


def test_ipython_display_adapter() -> None:
    obj = HTML("<h1>Hi</h1>")
    meta = dispatch_adapter(obj)
    assert meta["adapter_used"] == "IPythonDisplayAdapter"
    assert meta["metadata"]["type"] == "ipython_display"
    summary = deterministic_summary(meta)
    print("ipython_display:", summary)
    assert summary == "An IPython display object with representations: _repr_html_."
