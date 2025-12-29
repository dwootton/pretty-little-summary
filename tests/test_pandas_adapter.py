"""Tests for pandas adapter enhancements."""

import pytest

from pretty_little_summary.adapters import dispatch_adapter
from pretty_little_summary.descriptor_utils import format_bytes
from pretty_little_summary.synthesizer import deterministic_summary


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
    print("pandas_series:", summary)
    parts = [f"A pandas Series 'price' with {meta['metadata']['length']} values."]
    null_count = meta["metadata"].get("null_count")
    if null_count is not None:
        parts.append(f"Nulls: {null_count}.")
    dtype = meta["metadata"].get("dtype")
    if dtype:
        parts.append(f"Dtype: {dtype}.")
    stats = meta["metadata"].get("stats")
    if stats:
        parts.append(f"Stats: {stats}.")
    sample_values = meta["metadata"].get("sample_values")
    if sample_values:
        parts.append(f"Sample: [{', '.join(sample_values)}].")
    assert summary == " ".join(parts)


def test_pandas_dataframe_metadata() -> None:
    df = pd.DataFrame({"a": [1, 2, None], "b": ["x", "y", "z"]})
    meta = dispatch_adapter(df)
    assert meta["adapter_used"] == "PandasAdapter"
    assert meta["metadata"]["type"] == "dataframe"
    assert meta["metadata"]["rows"] == 3
    assert meta["metadata"]["columns"] == 2
    assert "column_analysis" in meta["metadata"]
    summary = deterministic_summary(meta)
    print("pandas_df:", summary)
    parts = [
        f"A pandas DataFrame with {meta['metadata']['rows']} rows and {meta['metadata']['columns']} columns."
    ]
    null_count = meta["metadata"].get("null_count")
    if null_count is not None:
        parts.append(f"Nulls: {null_count}.")
    memory_bytes = meta["metadata"].get("memory_bytes")
    if memory_bytes is not None:
        parts.append(f"Memory: {format_bytes(memory_bytes)}.")
    col_analysis = meta["metadata"].get("column_analysis") or []
    if col_analysis:
        cols = []
        for col in col_analysis[:3]:
            name = col.get("name")
            dtype = col.get("dtype")
            col_nulls = col.get("null_count")
            stats = col.get("stats")
            cardinality = col.get("cardinality")
            details = []
            if dtype:
                details.append(dtype)
            if col_nulls:
                details.append(f"{col_nulls} nulls")
            if stats:
                details.append(f"stats: {stats}")
            elif cardinality:
                details.append(f"cardinality: {cardinality}")
            cols.append(f"{name} ({', '.join(details)})" if details else f"{name}")
        if cols:
            parts.append(f"Columns: {', '.join(cols)}.")
    sample_rows = meta["metadata"].get("sample_rows")
    if sample_rows:
        parts.append(f"Sample row: {sample_rows[0]}.")
    elif meta["metadata"].get("sample_rows_omitted"):
        parts.append("Sample rows omitted for size/perf.")
    assert summary == " ".join(parts)


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
    idx = pd.Index([1, 2, 3], name="ids")
    meta = dispatch_adapter(idx)
    assert meta["metadata"]["type"] == "index"
    summary = deterministic_summary(meta)
    print("pandas_index:", summary)
    assert summary == "A pandas Index with 3 entries."


def test_pandas_categorical() -> None:
    cat = pd.Categorical(["a", "b", "a"])
    meta = dispatch_adapter(cat)
    assert meta["metadata"]["type"] == "categorical"
    summary = deterministic_summary(meta)
    print("pandas_cat:", summary)
    assert summary == "A pandas Categorical with 2 categories."
