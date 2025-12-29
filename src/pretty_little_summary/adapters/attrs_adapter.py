"""Adapter for attrs classes."""

from __future__ import annotations

from typing import Any

try:
    import attr
    LIBRARY_AVAILABLE = True
except ImportError:
    LIBRARY_AVAILABLE = False

from pretty_little_summary.adapters._base import AdapterRegistry
from pretty_little_summary.core import MetaDescription
from pretty_little_summary.descriptor_utils import safe_repr


class AttrsAdapter:
    """Adapter for attrs-based classes."""

    @staticmethod
    def can_handle(obj: Any) -> bool:
        if not LIBRARY_AVAILABLE:
            return False
        try:
            return attr.has(type(obj))
        except Exception:
            return False

    @staticmethod
    def extract_metadata(obj: Any) -> MetaDescription:
        meta: MetaDescription = {
            "object_type": f"{type(obj).__module__}.{type(obj).__name__}",
            "adapter_used": "AttrsAdapter",
        }
        metadata: dict[str, Any] = {}
        try:
            metadata.update(_describe_attrs(obj))
        except Exception as e:
            meta["warnings"] = [f"AttrsAdapter failed: {e}"]

        if metadata:
            meta["metadata"] = metadata
            meta["nl_summary"] = _build_nl_summary(metadata)
        return meta


def _describe_attrs(obj: Any) -> dict[str, Any]:
    attrs = attr.fields(type(obj))
    values = {a.name: safe_repr(getattr(obj, a.name), 50) for a in attrs}
    return {
        "type": "attrs",
        "class_name": type(obj).__name__,
        "fields": [a.name for a in attrs],
        "values": values,
    }


if LIBRARY_AVAILABLE:
    AdapterRegistry.register(AttrsAdapter)


def _build_nl_summary(metadata: dict[str, Any]) -> str:
    class_name = metadata.get("class_name")
    fields = metadata.get("fields") or []
    return f"An attrs class {class_name} with {len(fields)} attributes."
