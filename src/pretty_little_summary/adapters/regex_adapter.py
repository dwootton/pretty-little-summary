"""Adapter for regex patterns and matches."""

from __future__ import annotations

import re
from typing import Any

from pretty_little_summary.adapters._base import AdapterRegistry
from pretty_little_summary.core import MetaDescription


class RegexAdapter:
    """Adapter for compiled regex patterns and match objects."""

    @staticmethod
    def can_handle(obj: Any) -> bool:
        return isinstance(obj, (re.Pattern, re.Match))

    @staticmethod
    def extract_metadata(obj: Any) -> MetaDescription:
        meta: MetaDescription = {
            "object_type": f"{type(obj).__module__}.{type(obj).__name__}",
            "adapter_used": "RegexAdapter",
        }

        metadata: dict[str, Any] = {}
        if isinstance(obj, re.Pattern):
            metadata.update(_describe_pattern(obj))
        elif isinstance(obj, re.Match):
            metadata.update(_describe_match(obj))

        if metadata:
            meta["metadata"] = metadata
            meta["nl_summary"] = _build_nl_summary(metadata)
        return meta


def _describe_pattern(pattern: re.Pattern) -> dict[str, Any]:
    flags = _format_flags(pattern.flags)
    return {
        "type": "regex_pattern",
        "pattern": pattern.pattern,
        "flags": flags,
        "groups": pattern.groups,
        "groupindex": pattern.groupindex,
    }


def _describe_match(match: re.Match) -> dict[str, Any]:
    start, end = match.span()
    return {
        "type": "regex_match",
        "match": match.group(0),
        "span": (start, end),
        "groups": match.groups(),
        "groupdict": match.groupdict(),
    }


def _format_flags(flags: int) -> list[str]:
    flag_names = []
    for name in ["IGNORECASE", "MULTILINE", "DOTALL", "VERBOSE", "ASCII"]:
        if flags & getattr(re, name):
            flag_names.append(name)
    return flag_names


AdapterRegistry.register(RegexAdapter)


def _build_nl_summary(metadata: dict[str, Any]) -> str:
    rtype = metadata.get("type")
    if rtype == "regex_pattern":
        pattern = metadata.get("pattern")
        flags = metadata.get("flags") or []
        parts = [f"A compiled regex pattern /{pattern}/."]
        if flags:
            parts.append(f"Flags: {', '.join(flags)}.")
        groups = metadata.get("groups")
        if groups:
            parts.append(f"{groups} capturing groups.")
        return " ".join(parts)
    if rtype == "regex_match":
        match = metadata.get("match")
        span = metadata.get("span")
        if span:
            return f"A regex match result: matched '{match}' at position {span[0]}:{span[1]}."
        return f"A regex match result: matched '{match}'."
    return "A regex object."
