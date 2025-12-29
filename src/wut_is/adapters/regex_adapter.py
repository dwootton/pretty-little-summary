"""Adapter for regex patterns and matches."""

from __future__ import annotations

import re
from typing import Any

from wut_is.adapters._base import AdapterRegistry
from wut_is.core import MetaDescription


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
