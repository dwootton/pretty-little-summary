"""Adapter for Plotly figures."""

from __future__ import annotations

from typing import Any

try:
    import plotly.graph_objs as go
    LIBRARY_AVAILABLE = True
except ImportError:
    LIBRARY_AVAILABLE = False

from pretty_little_summary.adapters._base import AdapterRegistry
from pretty_little_summary.core import MetaDescription


class PlotlyAdapter:
    """Adapter for plotly.graph_objs.Figure."""

    @staticmethod
    def can_handle(obj: Any) -> bool:
        if not LIBRARY_AVAILABLE:
            return False
        try:
            return isinstance(obj, go.Figure)
        except Exception:
            return False

    @staticmethod
    def extract_metadata(obj: Any) -> MetaDescription:
        meta: MetaDescription = {
            "object_type": f"{type(obj).__module__}.{type(obj).__name__}",
            "adapter_used": "PlotlyAdapter",
        }
        metadata: dict[str, Any] = {"type": "plotly_figure"}
        try:
            metadata["traces"] = len(obj.data)
            metadata["trace_types"] = [trace.type for trace in obj.data[:5]]
            metadata["title"] = getattr(obj.layout, "title", {}).text if obj.layout else None
            metadata["has_frames"] = bool(getattr(obj, "frames", []))
            if obj.layout:
                metadata["xaxis_title"] = getattr(obj.layout.xaxis, "title", {}).text
                metadata["yaxis_title"] = getattr(obj.layout.yaxis, "title", {}).text
        except Exception:
            pass
        meta["metadata"] = metadata
        meta["nl_summary"] = _build_nl_summary(metadata)
        return meta


if LIBRARY_AVAILABLE:
    AdapterRegistry.register(PlotlyAdapter)


def _build_nl_summary(metadata: dict[str, Any]) -> str:
    return f"A Plotly figure with {metadata.get('traces')} traces."
