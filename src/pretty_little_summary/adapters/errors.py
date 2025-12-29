"""Adapters for exceptions and tracebacks."""

from __future__ import annotations

import traceback as tb
import types
from typing import Any

from pretty_little_summary.adapters._base import AdapterRegistry
from pretty_little_summary.core import MetaDescription


class ErrorAdapter:
    """Adapter for BaseException and traceback objects."""

    @staticmethod
    def can_handle(obj: Any) -> bool:
        return isinstance(obj, BaseException) or isinstance(obj, types.TracebackType)

    @staticmethod
    def extract_metadata(obj: Any) -> MetaDescription:
        meta: MetaDescription = {
            "object_type": f"{type(obj).__module__}.{type(obj).__name__}",
            "adapter_used": "ErrorAdapter",
        }
        metadata: dict[str, Any] = {}
        if isinstance(obj, BaseException):
            metadata.update(_describe_exception(obj))
        elif isinstance(obj, types.TracebackType):
            metadata.update(_describe_traceback(obj))
        if metadata:
            meta["metadata"] = metadata
            meta["nl_summary"] = _build_nl_summary(metadata)
        return meta


def _describe_exception(exc: BaseException) -> dict[str, Any]:
    return {
        "type": "exception",
        "name": type(exc).__name__,
        "message": str(exc),
        "args": exc.args,
        "has_traceback": exc.__traceback__ is not None,
    }


def _describe_traceback(traceback_obj: types.TracebackType) -> dict[str, Any]:
    frames = []
    for frame in tb.extract_tb(traceback_obj):
        frames.append(
            {
                "filename": frame.filename,
                "line": frame.lineno,
                "name": frame.name,
                "code": frame.line,
            }
        )
    return {
        "type": "traceback",
        "depth": len(frames),
        "frames": frames[:5],
        "last_frame": frames[-1] if frames else None,
    }


AdapterRegistry.register(ErrorAdapter)


def _build_nl_summary(metadata: dict[str, Any]) -> str:
    if metadata.get("type") == "exception":
        return f"An {metadata.get('name')} exception: '{metadata.get('message')}'."
    if metadata.get("type") == "traceback":
        depth = metadata.get("depth")
        frames = metadata.get("frames", [])
        parts = [f"A traceback with {depth} frames (most recent last):"]
        for frame in frames:
            parts.append(
                f"→ {frame.get('filename')}:{frame.get('line')} in {frame.get('name')}()"
            )
        last = metadata.get("last_frame")
        if last and last.get("code"):
            parts.append(f"Last frame context: '{last.get('code')}'.")
        return "\n".join(parts)
    return "An error object."
