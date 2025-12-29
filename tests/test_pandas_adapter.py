"""Tests for pandas adapter enhancements."""

import pytest

from wut_is.adapters import dispatch_adapter
from wut_is.synthesizer import deterministic_summary


pd = pytest.importorskip("pandas")


def test_pandas_series_metadata() -> None:
    series = pd.Series([1, 2, 3, None], name="price")
    meta = dispatch_adapter(series)
    assert meta["adapter_used"] == "PandasAdapter"
    assert meta["metadata"]["type"] == "series"
    assert meta["metadata"]["length"] == 4
    assert meta["metadata"]["name"] == "price"
    assert "null_count" in meta["metadata"]
    summary = deterministic_summary(meta)
    assert "Nulls:" in summary


def test_pandas_dataframe_metadata() -> None:
    df = pd.DataFrame({"a": [1, 2, None], "b": ["x", "y", "z"]})
    meta = dispatch_adapter(df)
    assert meta["adapter_used"] == "PandasAdapter"
    assert meta["metadata"]["type"] == "dataframe"
    assert meta["metadata"]["rows"] == 3
    assert meta["metadata"]["columns"] == 2
    assert "column_analysis" in meta["metadata"]
    summary = deterministic_summary(meta)
    assert "Memory:" in summary


def test_pandas_series_sampling_limit_10k() -> None:
    series = pd.Series(range(10_000))
    meta = dispatch_adapter(series)
    assert meta["metadata"]["stats_sample_size"] == 10_000


def test_pandas_series_sampling_limit_100k() -> None:
    series = pd.Series(range(100_000))
    meta = dispatch_adapter(series)
    assert meta["metadata"]["stats_sample_size"] == 10_000


def test_pandas_dataframe_column_sampling_limit() -> None:
    df = pd.DataFrame({"a": range(100_000), "b": range(100_000)})
    meta = dispatch_adapter(df)
    col_meta = meta["metadata"]["column_analysis"][0]
    assert col_meta["stats_sample_size"] == 10_000
