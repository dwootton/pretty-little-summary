"""Adapter for Bokeh figures."""

from __future__ import annotations

from typing import Any

try:
    from bokeh.plotting.figure import Figure
    LIBRARY_AVAILABLE = True
except ImportError:
    LIBRARY_AVAILABLE = False

from pretty_little_summary.adapters._base import AdapterRegistry
from pretty_little_summary.core import MetaDescription


class BokehAdapter:
    """Adapter for bokeh.plotting.figure.Figure."""

    @staticmethod
    def can_handle(obj: Any) -> bool:
        if not LIBRARY_AVAILABLE:
            return False
        try:
            return isinstance(obj, Figure)
        except Exception:
            return False

    @staticmethod
    def extract_metadata(obj: Any) -> MetaDescription:
        meta: MetaDescription = {
            "object_type": f"{type(obj).__module__}.{type(obj).__name__}",
            "adapter_used": "BokehAdapter",
        }
        metadata: dict[str, Any] = {"type": "bokeh_figure"}
        try:
            metadata["renderers"] = len(obj.renderers)
            metadata["title"] = obj.title.text if obj.title else None
            metadata["xaxis_label"] = obj.xaxis[0].axis_label if obj.xaxis else None
            metadata["yaxis_label"] = obj.yaxis[0].axis_label if obj.yaxis else None
            metadata["tools"] = [tool.__class__.__name__ for tool in obj.tools[:5]]
        except Exception:
            pass
        meta["metadata"] = metadata
        meta["nl_summary"] = _build_nl_summary(metadata)
        return meta


if LIBRARY_AVAILABLE:
    AdapterRegistry.register(BokehAdapter)


def _build_nl_summary(metadata: dict[str, Any]) -> str:
    return f"A Bokeh figure with {metadata.get('renderers')} renderers."
