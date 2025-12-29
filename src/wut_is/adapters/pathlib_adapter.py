"""Adapter for pathlib Path and PurePath."""

from __future__ import annotations

from pathlib import Path, PurePath
from typing import Any

from wut_is.adapters._base import AdapterRegistry
from wut_is.core import MetaDescription
from wut_is.descriptor_utils import format_bytes


class PathlibAdapter:
    """Adapter for Path and PurePath objects."""

    @staticmethod
    def can_handle(obj: Any) -> bool:
        return isinstance(obj, PurePath)

    @staticmethod
    def extract_metadata(obj: Any) -> MetaDescription:
        meta: MetaDescription = {
            "object_type": f"{type(obj).__module__}.{type(obj).__name__}",
            "adapter_used": "PathlibAdapter",
        }

        metadata: dict[str, Any] = {
            "type": "path",
            "path": str(obj),
            "name": obj.name,
            "suffix": obj.suffix,
            "parts": list(obj.parts),
        }

        if isinstance(obj, Path):
            try:
                exists = obj.exists()
                metadata["exists"] = exists
                if exists:
                    metadata["is_file"] = obj.is_file()
                    metadata["is_dir"] = obj.is_dir()
                    if obj.is_file():
                        size = obj.stat().st_size
                        metadata["size_bytes"] = size
                        metadata["size"] = format_bytes(size)
            except Exception:
                pass
        else:
            metadata["pure"] = True

        meta["metadata"] = metadata
        meta["nl_summary"] = _build_nl_summary(metadata)
        return meta


AdapterRegistry.register(PathlibAdapter)


def _build_nl_summary(metadata: dict[str, Any]) -> str:
    path = metadata.get("path")
    pure = metadata.get("pure")
    if pure:
        return f"A pure path '{path}'."
    if metadata.get("exists") is True:
        if metadata.get("is_dir"):
            return f"A path '{path}' pointing to an existing directory."
        if metadata.get("is_file"):
            size = metadata.get("size")
            if size:
                return f"A path '{path}' pointing to an existing file ({size})."
            return f"A path '{path}' pointing to an existing file."
        return f"A path '{path}' pointing to an existing location."
    if metadata.get("exists") is False:
        return f"A path '{path}' pointing to a non-existent location."
    return f"A path '{path}'."
