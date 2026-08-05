"""Adapters for structured stdlib types (dataclass, namedtuple, enum)."""

from __future__ import annotations

import dataclasses
from enum import Enum
from typing import Any

from pretty_little_summary.adapters._base import AdapterRegistry
from pretty_little_summary.core import MetaDescription
from pretty_little_summary.descriptor_utils import safe_repr


class StructuredAdapter:
    """Adapter for dataclasses, namedtuples, and enums."""

    @staticmethod
    def can_handle(obj: Any) -> bool:
        if dataclasses.is_dataclass(obj) and not isinstance(obj, type):
            return True
        if _is_namedtuple(obj):
            return True
        if isinstance(obj, Enum):
            return True
        return False

    @staticmethod
    def extract_metadata(obj: Any) -> MetaDescription:
        meta: MetaDescription = {
            "object_type": f"{type(obj).__module__}.{type(obj).__name__}",
            "adapter_used": "StructuredAdapter",
        }

        metadata: dict[str, Any] = {}

        if dataclasses.is_dataclass(obj) and not isinstance(obj, type):
            metadata.update(_describe_dataclass(obj))
        elif _is_namedtuple(obj):
            metadata.update(_describe_namedtuple(obj))
        elif isinstance(obj, Enum):
            metadata.update(_describe_enum(obj))

        if metadata:
            meta["metadata"] = metadata
            meta["nl_summary"] = _build_nl_summary(metadata)
        return meta


def _build_nl_summary(metadata: dict[str, Any]) -> str:
    kind = metadata.get("type")
    class_name = metadata.get("class_name")
    if kind in ("dataclass", "namedtuple"):
        label = "A dataclass" if kind == "dataclass" else "A namedtuple"
        fields = metadata.get("fields", [])
        values = metadata.get("values", {})
        shown = fields[:8]
        pairs = ", ".join(f"{name}={values.get(name)}" for name in shown)
        suffix = f", ... ({len(fields)} fields total)" if len(fields) > 8 else ""
        return f"{label} {class_name} with fields: {pairs}{suffix}."
    if kind == "enum":
        members = metadata.get("members", [])
        member_word = "member" if len(members) == 1 else "members"
        return (
            f"An enum {class_name}: {metadata.get('name')} "
            f"(one of {len(members)} {member_word}: {', '.join(members)})."
        )
    return f"A structured object of type {kind}."


def _describe_dataclass(obj: Any) -> dict[str, Any]:
    fields = dataclasses.fields(obj)
    values = {
        f.name: safe_repr(getattr(obj, f.name), 50) for f in fields
    }
    return {
        "type": "dataclass",
        "class_name": type(obj).__name__,
        "fields": [f.name for f in fields],
        "values": values,
    }


def _describe_namedtuple(obj: Any) -> dict[str, Any]:
    values = {name: safe_repr(getattr(obj, name), 50) for name in obj._fields}
    return {
        "type": "namedtuple",
        "class_name": type(obj).__name__,
        "fields": list(obj._fields),
        "values": values,
    }


def _describe_enum(obj: Enum) -> dict[str, Any]:
    members = [member.name for member in type(obj)]
    return {
        "type": "enum",
        "class_name": type(obj).__name__,
        "name": obj.name,
        "value": safe_repr(obj.value, 50),
        "members": members,
    }


def _is_namedtuple(obj: Any) -> bool:
    return isinstance(obj, tuple) and hasattr(obj, "_fields")


AdapterRegistry.register(StructuredAdapter)
