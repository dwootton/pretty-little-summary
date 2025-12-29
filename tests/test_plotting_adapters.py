"""Tests for plotting adapters."""

import pytest

from pretty_little_summary.adapters import dispatch_adapter
from pretty_little_summary.synthesizer import deterministic_summary


plotly = pytest.importorskip("plotly.graph_objs")
from plotly import graph_objs as go  # noqa: E402


def test_plotly_adapter() -> None:
    fig = go.Figure(data=[go.Scatter(y=[1, 2, 3])])
    meta = dispatch_adapter(fig)
    assert meta["adapter_used"] == "PlotlyAdapter"
    assert meta["metadata"]["type"] == "plotly_figure"
    summary = deterministic_summary(meta)
    print("plotly:", summary)
    expected = f"A Plotly figure with {meta['metadata'].get('traces')} traces."
    assert summary == expected


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
    expected = f"A Bokeh figure with {meta['metadata'].get('renderers')} renderers."
    assert summary == expected


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
    expected = f"A seaborn {meta['metadata'].get('grid_type')} with {meta['metadata'].get('axes_count')} axes."
    assert summary == expected


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
    assert summary == "An Altair chart with mark 'line'."


matplotlib = pytest.importorskip("matplotlib")
import matplotlib.pyplot as plt  # noqa: E402


def test_matplotlib_adapter() -> None:
    fig, ax = plt.subplots()
    ax.plot([1, 2, 3], [3, 2, 1], label="series")
    meta = dispatch_adapter(fig)
    assert meta["adapter_used"] == "MatplotlibAdapter"
    summary = deterministic_summary(meta)
    print("mpl_fig:", summary)
    expected = f"A matplotlib figure with {meta.get('metadata', {}).get('num_subplots') or 'unknown'} subplots."
    assert summary == expected


def test_matplotlib_axes_inference() -> None:
    fig, ax = plt.subplots()
    ax.scatter([1, 2, 3], [3, 2, 1])
    ax.bar([1, 2, 3], [3, 2, 1])
    meta = dispatch_adapter(ax)
    assert meta["adapter_used"] == "MatplotlibAdapter"
    summary = deterministic_summary(meta)
    print("mpl_axes:", summary)
    assert summary == "A matplotlib axes with plotted elements."


def test_matplotlib_axes_image_hist() -> None:
    fig, ax = plt.subplots()
    ax.imshow([[0, 1], [1, 0]])
    ax.hist([1, 2, 2, 3, 3, 3])
    meta = dispatch_adapter(ax)
    summary = deterministic_summary(meta)
    print("mpl_axes_image_hist:", summary)
    assert summary == "A matplotlib axes with plotted elements."
