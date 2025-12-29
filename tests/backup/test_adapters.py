"""Tests for adapter system."""

import pytest

from pretty_little_summary.adapters import (
    AdapterRegistry,
    GenericAdapter,
    PandasAdapter,
    dispatch_adapter,
)


def test_generic_adapter_handles_anything():
    """GenericAdapter can handle any object."""
    assert GenericAdapter.can_handle("string") is True
    assert GenericAdapter.can_handle(123) is True
    assert GenericAdapter.can_handle([1, 2, 3]) is True


def test_generic_adapter_extracts_metadata():
    """GenericAdapter extracts basic metadata."""
    obj = {"a": 1, "b": 2}
    meta = GenericAdapter.extract_metadata(obj)

    assert "object_type" in meta
    assert "adapter_used" in meta
    assert meta["adapter_used"] == "GenericAdapter"
    assert "dict" in meta["object_type"]


def test_dispatch_adapter_uses_generic_fallback():
    """dispatch_adapter uses GenericAdapter for unknown types."""
    class CustomType:
        pass

    obj = CustomType()
    meta = dispatch_adapter(obj)

    assert meta["adapter_used"] == "GenericAdapter"
    assert "object_type" in meta


def test_pandas_adapter_with_dataframe():
    """PandasAdapter works with pandas DataFrame."""
    pd = pytest.importorskip("pandas")

    df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})

    assert PandasAdapter.can_handle(df) is True

    meta = PandasAdapter.extract_metadata(df)

    assert meta["object_type"] == "pandas.DataFrame"
    assert meta["adapter_used"] == "PandasAdapter"
    assert meta["shape"] == (3, 2)
    assert meta["columns"] == ["a", "b"]
    assert "dtypes" in meta


def test_pandas_adapter_with_series():
    """PandasAdapter works with pandas Series."""
    pd = pytest.importorskip("pandas")

    series = pd.Series([1, 2, 3, 4, 5])

    assert PandasAdapter.can_handle(series) is True

    meta = PandasAdapter.extract_metadata(series)

    assert meta["object_type"] == "pandas.Series"
    assert meta["adapter_used"] == "PandasAdapter"
    assert meta["shape"] == (5,)


def test_adapter_registry_priority():
    """AdapterRegistry respects priority order."""
    pd = pytest.importorskip("pandas")

    df = pd.DataFrame({"a": [1, 2, 3]})

    # Should match PandasAdapter, not GenericAdapter
    adapter = AdapterRegistry.get_adapter(df)
    assert adapter == PandasAdapter


def test_dispatch_adapter_with_dataframe():
    """dispatch_adapter correctly routes DataFrame to PandasAdapter."""
    pd = pytest.importorskip("pandas")

    df = pd.DataFrame({"x": [1, 2], "y": [3, 4]})
    meta = dispatch_adapter(df)

    assert meta["adapter_used"] == "PandasAdapter"
    assert meta["object_type"] == "pandas.DataFrame"
