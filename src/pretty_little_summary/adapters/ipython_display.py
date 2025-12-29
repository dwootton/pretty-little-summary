"""Adapter for IPython display objects."""

from __future__ import annotations

from typing import Any

try:
    from IPython.display import DisplayObject
    LIBRARY_AVAILABLE = True
except ImportError:
    LIBRARY_AVAILABLE = False

from pretty_little_summary.adapters._base import AdapterRegistry
from pretty_little_summary.core import MetaDescription


class IPythonDisplayAdapter:
    """Adapter for IPython display objects and rich reprs."""

    @staticmethod
    def can_handle(obj: Any) -> bool:
        if not LIBRARY_AVAILABLE:
            return False
        try:
            if isinstance(obj, DisplayObject):
                return True
        except Exception:
            return False
        return _has_rich_repr(obj)

    @staticmethod
    def extract_metadata(obj: Any) -> MetaDescription:
        meta: MetaDescription = {
            "object_type": f"{type(obj).__module__}.{type(obj).__name__}",
            "adapter_used": "IPythonDisplayAdapter",
        }
        metadata: dict[str, Any] = {"type": "ipython_display"}
        metadata["reprs"] = _available_repr_methods(obj)
        meta["metadata"] = metadata
        meta["nl_summary"] = _build_nl_summary(metadata)
        return meta


def _has_rich_repr(obj: Any) -> bool:
    return any(
        hasattr(obj, name)
        for name in (
            "_repr_html_",
            "_repr_png_",
            "_repr_svg_",
            "_repr_markdown_",
            "_repr_latex_",
        )
    )


def _available_repr_methods(obj: Any) -> list[str]:
    methods = []
    for name in (
        "_repr_html_",
        "_repr_png_",
        "_repr_svg_",
        "_repr_markdown_",
        "_repr_latex_",
    ):
        if hasattr(obj, name):
            methods.append(name)
    return methods


if LIBRARY_AVAILABLE:
    AdapterRegistry.register(IPythonDisplayAdapter)


def _build_nl_summary(metadata: dict[str, Any]) -> str:
    reprs = metadata.get("reprs") or []
    if reprs:
        return f"An IPython display object with representations: {', '.join(reprs)}."
    return "An IPython display object."
