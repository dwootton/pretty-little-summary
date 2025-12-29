"""Adapter for PyArrow tables."""

from __future__ import annotations

from typing import Any

try:
    import pyarrow as pa
    LIBRARY_AVAILABLE = True
except ImportError:
    LIBRARY_AVAILABLE = False

from wut_is.adapters._base import AdapterRegistry
from wut_is.core import MetaDescription
from wut_is.descriptor_utils import format_bytes


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
        meta: MetaDescription = {
            "object_type": f"{type(obj).__module__}.{type(obj).__name__}",
            "adapter_used": "PyArrowAdapter",
        }
        metadata: dict[str, Any] = {}
        try:
            metadata.update(_describe_table(obj))
            meta["shape"] = (obj.num_rows, obj.num_columns)
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
    return (
        f"A PyArrow Table with {metadata.get('rows')} rows and "
        f"{metadata.get('columns')} columns."
    )
