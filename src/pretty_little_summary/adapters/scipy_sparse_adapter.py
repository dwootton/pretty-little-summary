"""Adapter for scipy sparse matrices."""

from __future__ import annotations

from typing import Any

try:
    import scipy.sparse as sp
    LIBRARY_AVAILABLE = True
except ImportError:
    LIBRARY_AVAILABLE = False

from pretty_little_summary.adapters._base import AdapterRegistry
from pretty_little_summary.core import MetaDescription
from pretty_little_summary.descriptor_utils import compute_numeric_stats, format_bytes


class ScipySparseAdapter:
    """Adapter for scipy.sparse matrices."""

    @staticmethod
    def can_handle(obj: Any) -> bool:
        if not LIBRARY_AVAILABLE:
            return False
        try:
            return sp.issparse(obj)
        except Exception:
            return False

    @staticmethod
    def extract_metadata(obj: Any) -> MetaDescription:
        meta: MetaDescription = {
            "object_type": f"{type(obj).__module__}.{type(obj).__name__}",
            "adapter_used": "ScipySparseAdapter",
        }
        metadata: dict[str, Any] = {}

        try:
            metadata.update(_describe_sparse(obj))
            meta["shape"] = obj.shape
        except Exception as e:
            meta["warnings"] = [f"ScipySparseAdapter failed: {e}"]

        if metadata:
            meta["metadata"] = metadata
            meta["nl_summary"] = _build_nl_summary(metadata)
        return meta


def _describe_sparse(matrix: "sp.spmatrix") -> dict[str, Any]:
    rows, cols = matrix.shape
    nnz = int(matrix.nnz)
    density = nnz / (rows * cols) if rows and cols else 0.0
    data = matrix.data
    stats = None
    if data is not None and len(data) > 0:
        stats = compute_numeric_stats(data[:10000])

    return {
        "type": "sparse_matrix",
        "format": matrix.format,
        "rows": int(rows),
        "cols": int(cols),
        "nnz": nnz,
        "density": density,
        "stats": stats.to_prose() if stats else None,
        "memory_bytes": int(data.nbytes) if data is not None else None,
        "memory": format_bytes(int(data.nbytes)) if data is not None else None,
    }


if LIBRARY_AVAILABLE:
    AdapterRegistry.register(ScipySparseAdapter)


def _build_nl_summary(metadata: dict[str, Any]) -> str:
    return (
        f"A {metadata.get('format')} sparse matrix with shape "
        f"({metadata.get('rows')}, {metadata.get('cols')})."
    )
