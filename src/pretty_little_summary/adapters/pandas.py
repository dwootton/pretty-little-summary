"""Pandas adapter."""

from typing import Any

try:
    import pandas as pd
    LIBRARY_AVAILABLE = True
except ImportError:
    LIBRARY_AVAILABLE = False

from pretty_little_summary.adapters._base import AdapterRegistry
from pretty_little_summary.core import MetaDescription
from pretty_little_summary.descriptor_registry import DescribeConfigRegistry
from pretty_little_summary.descriptor_utils import (
    compute_cardinality,
    compute_numeric_stats,
    format_bytes,
    safe_repr,
)


class PandasAdapter:
    """Adapter for pandas DataFrame/Series."""

    @staticmethod
    def can_handle(obj: Any) -> bool:
        if not LIBRARY_AVAILABLE:
            return False
        try:
            return isinstance(
                obj,
                (
                    pd.DataFrame,
                    pd.Series,
                    pd.Index,
                    pd.MultiIndex,
                    pd.Timestamp,
                    pd.Categorical,
                ),
            )
        except Exception:
            return False

    @staticmethod
    def extract_metadata(obj: Any) -> MetaDescription:
        try:
            import pandas as pd

            config = DescribeConfigRegistry.get()
            meta: MetaDescription = {
                "object_type": f"pandas.{type(obj).__name__}",
                "adapter_used": "PandasAdapter",
            }
            metadata: dict[str, Any] = {}

            # Shape
            try:
                meta["shape"] = obj.shape
            except Exception as e:
                meta.setdefault("warnings", []).append(f"Could not get shape: {e}")

            # Columns (DataFrame only)
            if isinstance(obj, pd.DataFrame):
                try:
                    meta["columns"] = obj.columns.tolist()
                except Exception as e:
                    meta.setdefault("warnings", []).append(f"Could not get columns: {e}")

                # Dtypes
                try:
                    meta["dtypes"] = {col: str(dtype) for col, dtype in obj.dtypes.items()}
                except Exception as e:
                    meta.setdefault("warnings", []).append(f"Could not get dtypes: {e}")

                # Sample data (first 3 rows as markdown)
                try:
                    meta["sample_data"] = obj.head(3).to_markdown()
                except Exception:
                    # to_markdown might not be available
                    try:
                        meta["sample_data"] = obj.head(3).to_string()
                    except Exception as e:
                        meta.setdefault("warnings", []).append(
                            f"Could not get sample data: {e}"
                        )
                metadata.update(_describe_dataframe(obj, config))
            elif isinstance(obj, pd.Series):
                # Series
                try:
                    meta["dtypes"] = {"dtype": str(obj.dtype)}
                except Exception as e:
                    meta.setdefault("warnings", []).append(f"Could not get dtype: {e}")
                metadata.update(_describe_series(obj, config))
            elif isinstance(obj, pd.MultiIndex):
                metadata.update(_describe_multiindex(obj, config))
            elif isinstance(obj, pd.Index):
                metadata.update(_describe_index(obj, config))
            elif isinstance(obj, pd.Timestamp):
                metadata.update(_describe_timestamp(obj))
            elif isinstance(obj, pd.Categorical):
                metadata.update(_describe_categorical(obj))

            if metadata:
                meta["metadata"] = metadata
                meta["nl_summary"] = _build_nl_summary(meta, metadata)

            return meta

        except Exception as e:
            # Fallback to generic if adapter completely fails
            return {
                "object_type": f"{type(obj).__module__}.{type(obj).__name__}",
                "adapter_used": "PandasAdapter (failed)",
                "warnings": [f"Adapter failed: {e}"],
                "raw_repr": repr(obj)[:500],
            }



# Auto-register if library is available
if LIBRARY_AVAILABLE:
    AdapterRegistry.register(PandasAdapter)


def _describe_series(series: "pd.Series", config) -> dict[str, Any]:
    metadata: dict[str, Any] = {
        "type": "series",
        "length": int(series.shape[0]),
        "name": series.name if series.name is not None else None,
        "dtype": str(series.dtype),
    }

    try:
        metadata["index_type"] = type(series.index).__name__
        metadata["index_sample"] = [safe_repr(v, 50) for v in series.index[: config.sample_size]]
    except Exception:
        pass

    try:
        nulls = int(series.isna().sum())
        metadata["null_count"] = nulls
    except Exception:
        pass

    try:
        sample = series.head(config.sample_size).tolist()
        metadata["sample_values"] = [safe_repr(v, config.max_sample_repr) for v in sample]
    except Exception:
        pass

    if _is_numeric(series):
        try:
            samples = _sample_series_values(series, 10000)
            stats = compute_numeric_stats(samples)
            if stats:
                metadata["stats"] = stats.to_prose()
                metadata["stats_sample_size"] = len(samples)
        except Exception:
            pass
    else:
        try:
            samples = _sample_series_values(series, 10000)
            cardinality = compute_cardinality(samples)
            metadata["cardinality"] = cardinality.to_prose()
            metadata["cardinality_sample_size"] = len(samples)
        except Exception:
            pass

    return metadata


def _describe_dataframe(df: "pd.DataFrame", config) -> dict[str, Any]:
    metadata: dict[str, Any] = {
        "type": "dataframe",
        "rows": int(df.shape[0]),
        "columns": int(df.shape[1]),
    }

    try:
        metadata["index_type"] = type(df.index).__name__
        metadata["index_sample"] = [safe_repr(v, 50) for v in df.index[: config.sample_size]]
    except Exception:
        pass

    try:
        nulls = int(df.isna().sum().sum())
        metadata["null_count"] = nulls
    except Exception:
        pass

    try:
        memory = int(df.memory_usage(deep=True).sum())
        metadata["memory_bytes"] = memory
    except Exception:
        pass

    try:
        metadata["column_analysis"] = _analyze_columns(df, config)
    except Exception:
        pass

    try:
        rows = int(df.shape[0])
        cols = int(df.shape[1])
        if rows * cols <= config.max_sample_cells and rows <= config.max_sample_rows:
            sample = df.head(config.sample_size).to_dict(orient="records")
            metadata["sample_rows"] = _format_sample_rows(sample, config)
        else:
            metadata["sample_rows_omitted"] = True
    except Exception:
        pass

    return metadata


def _format_sample_rows(rows: list[dict[str, Any]], config) -> list[dict[str, Any]]:
    formatted: list[dict[str, Any]] = []
    for row in rows:
        formatted.append(
            {str(k): safe_repr(v, config.max_sample_repr) for k, v in row.items()}
        )
    return formatted


def _analyze_columns(df: "pd.DataFrame", config) -> list[dict[str, Any]]:
    analysis: list[dict[str, Any]] = []
    for col in list(df.columns)[: min(len(df.columns), 25)]:
        series = df[col]
        col_meta: dict[str, Any] = {
            "name": str(col),
            "dtype": str(series.dtype),
        }
        try:
            col_meta["null_count"] = int(series.isna().sum())
        except Exception:
            pass

        try:
            sample = series.head(config.sample_size).tolist()
            col_meta["sample_values"] = [safe_repr(v, config.max_sample_repr) for v in sample]
        except Exception:
            pass

        if _is_numeric(series):
            try:
                samples = _sample_series_values(series, 10000)
                stats = compute_numeric_stats(samples)
                if stats:
                    col_meta["stats"] = stats.to_prose()
                    col_meta["stats_sample_size"] = len(samples)
            except Exception:
                pass
        else:
            try:
                samples = _sample_series_values(series, 10000)
                cardinality = compute_cardinality(samples)
                col_meta["cardinality"] = cardinality.to_prose()
                col_meta["cardinality_sample_size"] = len(samples)
            except Exception:
                pass

        analysis.append(col_meta)
    return analysis


def _is_numeric(series: "pd.Series") -> bool:
    try:
        return series.dtype.kind in {"i", "u", "f"}
    except Exception:
        return False


def _sample_series_values(series: "pd.Series", limit: int) -> list[Any]:
    try:
        cleaned = series.dropna()
    except Exception:
        cleaned = series
    try:
        length = len(cleaned)
        if length > limit:
            return cleaned.sample(n=limit, random_state=0).tolist()
        return cleaned.tolist()
    except Exception:
        try:
            return cleaned.head(limit).tolist()
        except Exception:
            return []


def _describe_index(index: "pd.Index", config) -> dict[str, Any]:
    metadata: dict[str, Any] = {
        "type": "index",
        "length": int(len(index)),
        "dtype": str(index.dtype),
        "name": index.name,
        "is_unique": bool(index.is_unique),
    }
    try:
        metadata["sample_values"] = [safe_repr(v, 50) for v in index[: config.sample_size]]
    except Exception:
        pass
    return metadata


def _describe_multiindex(index: "pd.MultiIndex", config) -> dict[str, Any]:
    metadata: dict[str, Any] = {
        "type": "multiindex",
        "length": int(len(index)),
        "levels": int(index.nlevels),
        "names": list(index.names),
    }
    try:
        metadata["sample_values"] = [safe_repr(v, 50) for v in index[: config.sample_size]]
    except Exception:
        pass
    return metadata


def _describe_timestamp(value: "pd.Timestamp") -> dict[str, Any]:
    return {
        "type": "timestamp",
        "iso": value.isoformat(),
        "timezone": str(value.tzinfo) if value.tzinfo else None,
        "nanosecond": value.nanosecond,
    }


def _describe_categorical(cat: "pd.Categorical") -> dict[str, Any]:
    categories = list(cat.categories)
    counts = cat.value_counts().head(5).to_dict() if hasattr(cat, "value_counts") else None
    return {
        "type": "categorical",
        "length": len(cat),
        "categories": [safe_repr(v, 50) for v in categories[:10]],
        "ordered": bool(cat.ordered),
        "counts": counts,
    }


def _build_nl_summary(meta: MetaDescription, metadata: dict[str, Any]) -> str:
    obj_type = meta.get("object_type", "pandas")
    if metadata.get("type") == "dataframe":
        parts = [
            f"A pandas DataFrame with {metadata.get('rows')} rows and {metadata.get('columns')} columns."
        ]
        null_count = metadata.get("null_count")
        if null_count is not None:
            parts.append(f"Nulls: {null_count}.")
        memory_bytes = metadata.get("memory_bytes")
        if memory_bytes is not None:
            parts.append(f"Memory: {format_bytes(memory_bytes)}.")
        col_analysis = metadata.get("column_analysis") or []
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
        sample_rows = metadata.get("sample_rows")
        if sample_rows:
            parts.append(f"Sample row: {sample_rows[0]}.")
        elif metadata.get("sample_rows_omitted"):
            parts.append("Sample rows omitted for size/perf.")
        return " ".join(parts)
    if metadata.get("type") == "series":
        name = metadata.get("name") or "unnamed"
        parts = [f"A pandas Series '{name}' with {metadata.get('length')} values."]
        null_count = metadata.get("null_count")
        if null_count is not None:
            parts.append(f"Nulls: {null_count}.")
        dtype = metadata.get("dtype")
        if dtype:
            parts.append(f"Dtype: {dtype}.")
        stats = metadata.get("stats")
        if stats:
            parts.append(f"Stats: {stats}.")
        sample_values = metadata.get("sample_values")
        if sample_values:
            parts.append(f"Sample: [{', '.join(sample_values)}].")
        return " ".join(parts)
    if metadata.get("type") == "index":
        return f"A pandas Index with {metadata.get('length')} entries."
    if metadata.get("type") == "multiindex":
        return f"A pandas MultiIndex with {metadata.get('levels')} levels and {metadata.get('length')} entries."
    if metadata.get("type") == "timestamp":
        return f"A pandas Timestamp: {metadata.get('iso')}."
    if metadata.get("type") == "categorical":
        return f"A pandas Categorical with {len(metadata.get('categories', []))} categories."
    return f"A pandas object {obj_type}."
