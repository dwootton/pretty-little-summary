"""Adapters for callable objects, classes, and modules."""

from __future__ import annotations

import inspect
import types
from typing import Any

from pretty_little_summary.adapters._base import AdapterRegistry
from pretty_little_summary.core import MetaDescription
from pretty_little_summary.descriptor_utils import safe_repr


class CallableAdapter:
    """Adapter for functions, methods, classes, and modules."""

    @staticmethod
    def can_handle(obj: Any) -> bool:
        if inspect.isfunction(obj) or inspect.ismethod(obj):
            return True
        if isinstance(obj, type):
            return True
        if isinstance(obj, types.ModuleType):
            return True
        return False

    @staticmethod
    def extract_metadata(obj: Any) -> MetaDescription:
        meta: MetaDescription = {
            "object_type": f"{type(obj).__module__}.{type(obj).__name__}",
            "adapter_used": "CallableAdapter",
        }

        metadata: dict[str, Any] = {}

        if inspect.isfunction(obj):
            metadata.update(_describe_function(obj))
        elif inspect.ismethod(obj):
            metadata.update(_describe_method(obj))
        elif isinstance(obj, type):
            metadata.update(_describe_class(obj))
        elif isinstance(obj, types.ModuleType):
            metadata.update(_describe_module(obj))

        if metadata:
            meta["metadata"] = metadata
            meta["nl_summary"] = _build_nl_summary(metadata)
        return meta


def _describe_function(fn: Any) -> dict[str, Any]:
    return {
        "type": "function",
        "name": fn.__name__,
        "qualname": fn.__qualname__,
        "module": fn.__module__,
        "signature": str(inspect.signature(fn)),
        "is_lambda": fn.__name__ == "<lambda>",
        "doc": _first_line(fn.__doc__),
    }


def _describe_method(method: Any) -> dict[str, Any]:
    return {
        "type": "method",
        "name": method.__name__,
        "owner": type(method.__self__).__name__ if method.__self__ else None,
        "signature": str(inspect.signature(method)),
        "doc": _first_line(method.__doc__),
    }


def _describe_class(cls: type) -> dict[str, Any]:
    methods = [
        name
        for name in dir(cls)
        if not name.startswith("_") and callable(getattr(cls, name, None))
    ]
    signature = None
    try:
        signature = str(inspect.signature(cls.__init__))
    except (TypeError, ValueError):
        pass
    return {
        "type": "class",
        "name": cls.__name__,
        "module": cls.__module__,
        "bases": [base.__name__ for base in cls.__bases__],
        "methods": methods[:10],
        "init_signature": signature,
        "doc": _first_line(cls.__doc__),
    }


def _describe_module(module: types.ModuleType) -> dict[str, Any]:
    exports = [name for name in module.__dict__.keys() if not name.startswith("_")]
    return {
        "type": "module",
        "name": module.__name__,
        "file": getattr(module, "__file__", None),
        "is_package": hasattr(module, "__path__"),
        "exports_count": len(exports),
        "exports_sample": exports[:10],
        "doc": _first_line(module.__doc__),
    }


def _first_line(doc: str | None) -> str | None:
    if not doc:
        return None
    return doc.strip().splitlines()[0]


AdapterRegistry.register(CallableAdapter)


def _build_nl_summary(metadata: dict[str, Any]) -> str:
    return f"A callable {metadata.get('type')} named {metadata.get('name')}."
