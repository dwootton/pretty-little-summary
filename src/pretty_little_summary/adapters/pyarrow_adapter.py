"""Adapter for PyArrow tables."""

from __future__ import annotations

from typing import Any

try:
    import pyarrow as pa
    LIBRARY_AVAILABLE = True
except ImportError:
    LIBRARY_AVAILABLE = False

from pretty_little_summary.adapters._base import AdapterRegistry
from pretty_little_summary.core import MetaDescription
from pretty_little_summary.descriptor_registry import DescribeConfigRegistry
from pretty_little_summary.descriptor_utils import format_bytes, safe_repr


class PyArrowAdapter:
    """Adapter for pyarrow.Table."""

    @staticmethod
    def can_handle(obj: Any) -> bool:
        if not LIBRARY_AVAILABLE:
            return False
        try:
            return isinstance(obj, pa.Table)
        except Exception:
            return False

    @staticmethod
    def extract_metadata(obj: Any) -> MetaDescription:
        config = DescribeConfigRegistry.get()
        meta: MetaDescription = {
            "object_type": f"{type(obj).__module__}.{type(obj).__name__}",
            "adapter_used": "PyArrowAdapter",
        }
        metadata: dict[str, Any] = {}
        try:
            metadata.update(_describe_table(obj))
            meta["shape"] = (obj.num_rows, obj.num_columns)
            try:
                rows = obj.num_rows
                cols = obj.num_columns
                if rows * cols <= config.max_sample_cells and rows <= config.max_sample_rows:
                    sample = obj.slice(0, min(config.sample_size, rows)).to_pylist()
                    metadata["sample_rows"] = [
                        {str(k): safe_repr(v, config.max_sample_repr) for k, v in row.items()}
                        for row in sample
                    ]
                else:
                    metadata["sample_rows_omitted"] = True
            except Exception:
                pass
        except Exception as e:
            meta["warnings"] = [f"PyArrowAdapter failed: {e}"]

        if metadata:
            meta["metadata"] = metadata
            meta["nl_summary"] = _build_nl_summary(metadata)
        return meta


def _describe_table(table: "pa.Table") -> dict[str, Any]:
    schema = {field.name: str(field.type) for field in table.schema}
    size = table.nbytes
    return {
        "type": "pyarrow_table",
        "rows": table.num_rows,
        "columns": table.num_columns,
        "schema": schema,
        "memory_bytes": size,
        "memory": format_bytes(size),
    }


if LIBRARY_AVAILABLE:
    AdapterRegistry.register(PyArrowAdapter)


def _build_nl_summary(metadata: dict[str, Any]) -> str:
    parts = [
        f"A PyArrow Table with {metadata.get('rows')} rows and {metadata.get('columns')} columns."
    ]
    schema = metadata.get("schema") or {}
    if schema:
        cols = []
        for name, dtype in list(schema.items())[:3]:
            cols.append(f"{name} ({dtype})")
        if cols:
            parts.append(f"Schema: {', '.join(cols)}.")
    memory = metadata.get("memory")
    if memory:
        parts.append(f"Memory: {memory}.")
    sample_rows = metadata.get("sample_rows")
    if sample_rows:
        parts.append(f"Sample row: {sample_rows[0]}.")
    elif metadata.get("sample_rows_omitted"):
        parts.append("Sample rows omitted for size/perf.")
    return " ".join(parts)
