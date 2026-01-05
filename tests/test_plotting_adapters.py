"""Tests for plotting adapters."""

import pytest

from pretty_little_summary.adapters import dispatch_adapter
from pretty_little_summary.synthesizer import deterministic_summary
from tests.input import build_input, expected_output, load_example


plotly = pytest.importorskip("plotly.graph_objs")


def test_plotly_adapter() -> None:
    example = load_example("plotly_adapter")
    meta = dispatch_adapter(build_input(example))
    assert meta["adapter_used"] == "PlotlyAdapter"
    assert meta["metadata"]["type"] == "plotly_figure"
    summary = deterministic_summary(meta)
    print("plotly:", summary)
    assert summary == expected_output(example, meta)


bokeh_plotting = pytest.importorskip("bokeh.plotting")


def test_bokeh_adapter() -> None:
    example = load_example("bokeh_adapter")
    meta = dispatch_adapter(build_input(example))
    assert meta["adapter_used"] == "BokehAdapter"
    assert meta["metadata"]["type"] == "bokeh_figure"
    summary = deterministic_summary(meta)
    print("bokeh:", summary)
    assert summary == expected_output(example, meta)


seaborn = pytest.importorskip("seaborn")


def test_seaborn_adapter() -> None:
    example = load_example("seaborn_adapter")
    meta = dispatch_adapter(build_input(example))
    assert meta["adapter_used"] == "SeabornAdapter"
    assert meta["metadata"]["type"] == "seaborn_grid"
    summary = deterministic_summary(meta)
    print("seaborn:", summary)
    assert summary == expected_output(example, meta)


altair = pytest.importorskip("altair")


def test_altair_adapter() -> None:
    example = load_example("altair_adapter")
    meta = dispatch_adapter(build_input(example))
    assert meta["adapter_used"] == "AltairAdapter"
    assert meta["chart_type"] == "line"
    summary = deterministic_summary(meta)
    print("altair:", summary)
    assert summary == expected_output(example, meta)


matplotlib = pytest.importorskip("matplotlib")


def test_matplotlib_adapter() -> None:
    example = load_example("matplotlib_adapter")
    meta = dispatch_adapter(build_input(example))
    assert meta["adapter_used"] == "MatplotlibAdapter"
    summary = deterministic_summary(meta)
    print("mpl_fig:", summary)
    assert summary == expected_output(example, meta)


def test_matplotlib_axes_inference() -> None:
    example = load_example("matplotlib_axes_inference")
    meta = dispatch_adapter(build_input(example))
    assert meta["adapter_used"] == "MatplotlibAdapter"
    summary = deterministic_summary(meta)
    print("mpl_axes:", summary)
    assert summary == expected_output(example, meta)


def test_matplotlib_axes_image_hist() -> None:
    example = load_example("matplotlib_axes_image_hist")
    meta = dispatch_adapter(build_input(example))
    summary = deterministic_summary(meta)
    print("mpl_axes_image_hist:", summary)
    assert summary == expected_output(example, meta)
