"""Adapter for IO buffers and file handles."""

from __future__ import annotations

import io
from typing import Any

from pretty_little_summary.adapters._base import AdapterRegistry
from pretty_little_summary.core import MetaDescription
from pretty_little_summary.descriptor_utils import format_bytes


class IOAdapter:
    """Adapter for IO-related objects."""

    @staticmethod
    def can_handle(obj: Any) -> bool:
        if isinstance(obj, (io.BytesIO, io.StringIO)):
            return True
        if hasattr(obj, "mode") and hasattr(obj, "read"):
            return True
        return False

    @staticmethod
    def extract_metadata(obj: Any) -> MetaDescription:
        meta: MetaDescription = {
            "object_type": f"{type(obj).__module__}.{type(obj).__name__}",
            "adapter_used": "IOAdapter",
        }

        metadata: dict[str, Any] = {}
        if isinstance(obj, io.BytesIO):
            metadata.update(_describe_bytesio(obj))
        elif isinstance(obj, io.StringIO):
            metadata.update(_describe_stringio(obj))
        else:
            metadata.update(_describe_file(obj))

        if metadata:
            meta["metadata"] = metadata
            meta["nl_summary"] = _build_nl_summary(metadata)
        return meta


def _describe_bytesio(obj: io.BytesIO) -> dict[str, Any]:
    try:
        length = obj.getbuffer().nbytes
    except Exception:
        length = len(obj.getvalue())
    metadata: dict[str, Any] = {
        "type": "bytesio",
        "length": length,
        "size": format_bytes(length),
    }
    try:
        metadata["position"] = obj.tell()
    except Exception:
        pass
    return metadata


def _describe_stringio(obj: io.StringIO) -> dict[str, Any]:
    value = obj.getvalue()
    metadata: dict[str, Any] = {
        "type": "stringio",
        "length": len(value),
    }
    try:
        metadata["position"] = obj.tell()
    except Exception:
        pass
    return metadata


def _describe_file(obj: Any) -> dict[str, Any]:
    metadata: dict[str, Any] = {"type": "file"}
    try:
        metadata["name"] = obj.name
        metadata["mode"] = obj.mode
        metadata["closed"] = obj.closed
    except Exception:
        pass

    try:
        metadata["readable"] = obj.readable()
        metadata["writable"] = obj.writable()
        metadata["seekable"] = obj.seekable()
    except Exception:
        pass

    if hasattr(obj, "encoding"):
        metadata["encoding"] = obj.encoding

    try:
        if not obj.closed:
            metadata["position"] = obj.tell()
    except Exception:
        pass

    return metadata


AdapterRegistry.register(IOAdapter)


def _build_nl_summary(metadata: dict[str, Any]) -> str:
    itype = metadata.get("type")
    if itype == "bytesio":
        length = metadata.get("length")
        return f"An in-memory bytes buffer of {length} bytes."
    if itype == "stringio":
        length = metadata.get("length")
        return f"An in-memory text buffer of {length} characters."
    if itype == "file":
        name = metadata.get("name") or "unknown"
        mode = metadata.get("mode") or ""
        closed = metadata.get("closed")
        is_binary = "b" in mode
        status = "closed" if closed else "open"
        ftype = "binary" if is_binary else "text"
        return f"An {status} {ftype} file handle for '{name}'."
    return "An IO object."
