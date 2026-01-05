"""Tests for pandas adapter enhancements."""

import pytest

from pretty_little_summary.adapters import dispatch_adapter
from pretty_little_summary.synthesizer import deterministic_summary
from tests.input import build_input, expected_output, load_example


pd = pytest.importorskip("pandas")


def test_pandas_series_metadata() -> None:
    example = load_example("pandas_series_metadata")
    meta = dispatch_adapter(build_input(example))
    assert meta["adapter_used"] == "PandasAdapter"
    assert meta["metadata"]["type"] == "series"
    assert meta["metadata"]["length"] == 4
    assert meta["metadata"]["name"] == "price"
    assert "null_count" in meta["metadata"]
    summary = deterministic_summary(meta)
    print("pandas_series:", summary)
    assert summary == expected_output(example, meta)


def test_pandas_dataframe_metadata() -> None:
    example = load_example("pandas_dataframe_metadata")
    meta = dispatch_adapter(build_input(example))
    assert meta["adapter_used"] == "PandasAdapter"
    assert meta["metadata"]["type"] == "dataframe"
    assert meta["metadata"]["rows"] == 3
    assert meta["metadata"]["columns"] == 2
    assert "column_analysis" in meta["metadata"]
    summary = deterministic_summary(meta)
    print("pandas_df:", summary)
    assert summary == expected_output(example, meta)


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


def test_pandas_index_types() -> None:
    example = load_example("pandas_index_types")
    meta = dispatch_adapter(build_input(example))
    assert meta["metadata"]["type"] == "index"
    summary = deterministic_summary(meta)
    print("pandas_index:", summary)
    assert summary == expected_output(example, meta)


def test_pandas_categorical() -> None:
    example = load_example("pandas_categorical")
    meta = dispatch_adapter(build_input(example))
    assert meta["metadata"]["type"] == "categorical"
    summary = deterministic_summary(meta)
    print("pandas_cat:", summary)
    assert summary == expected_output(example, meta)
