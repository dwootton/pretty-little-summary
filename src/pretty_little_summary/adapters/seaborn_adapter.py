"""Adapter for seaborn grid objects."""

from __future__ import annotations

from typing import Any

try:
    import seaborn as sns
    LIBRARY_AVAILABLE = True
except ImportError:
    LIBRARY_AVAILABLE = False

from pretty_little_summary.adapters._base import AdapterRegistry
from pretty_little_summary.core import MetaDescription


class SeabornAdapter:
    """Adapter for seaborn FacetGrid/PairGrid/JointGrid."""

    @staticmethod
    def can_handle(obj: Any) -> bool:
        if not LIBRARY_AVAILABLE:
            return False
        try:
            return isinstance(obj, (sns.FacetGrid, sns.PairGrid, sns.JointGrid))
        except Exception:
            return False

    @staticmethod
    def extract_metadata(obj: Any) -> MetaDescription:
        meta: MetaDescription = {
            "object_type": f"{type(obj).__module__}.{type(obj).__name__}",
            "adapter_used": "SeabornAdapter",
        }
        metadata: dict[str, Any] = {"type": "seaborn_grid"}
        try:
            metadata["grid_type"] = type(obj).__name__
            metadata["axes_count"] = len(obj.axes.flat) if hasattr(obj, "axes") else None
            metadata["row_names"] = getattr(obj, "row_names", None)
            metadata["col_names"] = getattr(obj, "col_names", None)
            metadata["hue_names"] = getattr(obj, "hue_names", None)
            metadata["data_rows"] = len(obj.data) if hasattr(obj, "data") else None
        except Exception:
            pass
        meta["metadata"] = metadata
        meta["nl_summary"] = _build_nl_summary(metadata)
        return meta


if LIBRARY_AVAILABLE:
    AdapterRegistry.register(SeabornAdapter)


def _build_nl_summary(metadata: dict[str, Any]) -> str:
    grid = metadata.get("grid_type") or "grid"
    return f"A seaborn {grid} with {metadata.get('axes_count')} axes."
