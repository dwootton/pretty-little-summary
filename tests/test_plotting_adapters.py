"""Tests for plotting adapters."""

import pytest

from wut_is.adapters import dispatch_adapter
from wut_is.synthesizer import deterministic_summary


plotly = pytest.importorskip("plotly.graph_objs")
from plotly import graph_objs as go  # noqa: E402


def test_plotly_adapter() -> None:
    fig = go.Figure(data=[go.Scatter(y=[1, 2, 3])])
    meta = dispatch_adapter(fig)
    assert meta["adapter_used"] == "PlotlyAdapter"
    assert meta["metadata"]["type"] == "plotly_figure"
    summary = deterministic_summary(meta)
    print("plotly:", summary)
    assert "Plotly figure with" in summary


bokeh_plotting = pytest.importorskip("bokeh.plotting")
from bokeh.plotting import figure  # noqa: E402


def test_bokeh_adapter() -> None:
    fig = figure()
    fig.line([1, 2], [3, 4])
    meta = dispatch_adapter(fig)
    assert meta["adapter_used"] == "BokehAdapter"
    assert meta["metadata"]["type"] == "bokeh_figure"
    summary = deterministic_summary(meta)
    print("bokeh:", summary)
    assert "Bokeh figure" in summary


seaborn = pytest.importorskip("seaborn")
import pandas as pd  # noqa: E402


def test_seaborn_adapter() -> None:
    df = pd.DataFrame({"x": [1, 2, 3], "y": [3, 4, 5], "group": ["a", "a", "b"]})
    grid = seaborn.FacetGrid(df, col="group")
    meta = dispatch_adapter(grid)
    assert meta["adapter_used"] == "SeabornAdapter"
    assert meta["metadata"]["type"] == "seaborn_grid"
    summary = deterministic_summary(meta)
    print("seaborn:", summary)
    assert "seaborn" in summary


altair = pytest.importorskip("altair")


def test_altair_adapter() -> None:
    chart = altair.Chart(pd.DataFrame({"x": [1, 2], "y": [3, 4]})).mark_line().encode(
        x="x", y="y"
    )
    meta = dispatch_adapter(chart)
    assert meta["adapter_used"] == "AltairAdapter"
    assert meta["chart_type"] == "line"
    summary = deterministic_summary(meta)
    print("altair:", summary)
    assert "Altair chart" in summary


matplotlib = pytest.importorskip("matplotlib")
import matplotlib.pyplot as plt  # noqa: E402


def test_matplotlib_adapter() -> None:
    fig, ax = plt.subplots()
    ax.plot([1, 2, 3], [3, 2, 1], label="series")
    meta = dispatch_adapter(fig)
    assert meta["adapter_used"] == "MatplotlibAdapter"
    summary = deterministic_summary(meta)
    print("mpl_fig:", summary)
    assert "matplotlib figure" in summary


def test_matplotlib_axes_inference() -> None:
    fig, ax = plt.subplots()
    ax.scatter([1, 2, 3], [3, 2, 1])
    ax.bar([1, 2, 3], [3, 2, 1])
    meta = dispatch_adapter(ax)
    assert meta["adapter_used"] == "MatplotlibAdapter"
    summary = deterministic_summary(meta)
    print("mpl_axes:", summary)
    assert "matplotlib axes" in summary


def test_matplotlib_axes_image_hist() -> None:
    fig, ax = plt.subplots()
    ax.imshow([[0, 1], [1, 0]])
    ax.hist([1, 2, 2, 3, 3, 3])
    meta = dispatch_adapter(ax)
    summary = deterministic_summary(meta)
    print("mpl_axes_image_hist:", summary)
    assert "matplotlib axes" in summary
