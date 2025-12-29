"""Tests for IPython display adapter."""

import pytest

from wut_is.adapters import dispatch_adapter
from wut_is.synthesizer import deterministic_summary


ipython = pytest.importorskip("IPython")
from IPython.display import HTML  # noqa: E402


def test_ipython_display_adapter() -> None:
    obj = HTML("<h1>Hi</h1>")
    meta = dispatch_adapter(obj)
    assert meta["adapter_used"] == "IPythonDisplayAdapter"
    assert meta["metadata"]["type"] == "ipython_display"
    print("ipython_display:", deterministic_summary(meta))
    assert "IPython display object" in deterministic_summary(meta)
