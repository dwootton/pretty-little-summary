"""Text file sniffers: structured formats plus a plain-text fallback.

Structured-format detection (JSON/YAML/XML/CSV) is shared with the string
adapter via :func:`text_formats._detect_format`, so a ``.json`` *file* and a
JSON *string* are described consistently. JSONL and file-level facts (encoding,
line counts) are added here.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from pretty_little_summary.adapters.text_formats import _detect_format
from pretty_little_summary.core import MetaDescription
from pretty_little_summary.descriptor_utils import format_bytes
from pretty_little_summary.sniffers._base import (
    HEAD_BYTES,
    PRIORITY_FALLBACK,
    PRIORITY_TEXT,
    SnifferRegistry,
)

# Bytes that effectively never appear in text files; their presence means binary.
_TEXT_CONTROL_ALLOWED = {0x09, 0x0A, 0x0D, 0x0C}  # tab, LF, CR, form-feed

# tomllib is stdlib on Python 3.11+. When it is missing we can still recognise
# a .toml file by suffix, we just can't parse it for its keys.
try:
    import tomllib
except ImportError:  # pragma: no cover - depends on interpreter version
    tomllib = None


def _decode(head: bytes) -> str | None:
    """Decode a byte head as text, or return None if it looks binary."""
    if b"\x00" in head:
        return None
    control = sum(
        1 for b in head if b < 0x20 and b not in _TEXT_CONTROL_ALLOWED
    )
    if head and control / len(head) > 0.02:
        return None
    for encoding in ("utf-8", "latin-1"):
        try:
            return head.decode(encoding)
        except UnicodeDecodeError:
            continue
    return None


def _file_size(path: Path) -> int | None:
    try:
        return path.stat().st_size
    except OSError:
        return None


def _base_text_meta(path: Path, sniffer_name: str, text: str, truncated: bool) -> MetaDescription:
    size = _file_size(path)
    md: dict[str, Any] = {"path": str(path), "name": path.name}
    if size is not None:
        md["size_bytes"] = size
        md["size"] = format_bytes(size)
    lines = text.splitlines()
    md["sampled_line_count"] = len(lines)
    md["truncated_sample"] = truncated
    meta: MetaDescription = {
        "object_type": "builtins.file",
        "adapter_used": sniffer_name,
        "metadata": md,
    }
    return meta


# A line that looks like a TOML assignment (``key = value``) or a table header
# (``[section]``/``[[array]]``). Used only as a cheap content heuristic when the
# file lacks a .toml suffix.
_TOML_LINE = re.compile(r"^\s*(\[.+\]|[\w.\"'-]+\s*=)", re.MULTILINE)


class TomlSniffer:
    name = "TomlSniffer"

    @staticmethod
    def can_sniff(path: Path, head: bytes) -> bool:
        if path.suffix.lower() == ".toml":
            return True
        # No suffix hint: require both a structural match and, when tomllib is
        # available, that the sample actually parses as TOML.
        if tomllib is None:
            return False
        text = _decode(head)
        if text is None or not _TOML_LINE.search(text):
            return False
        try:
            tomllib.loads(text)
        except tomllib.TOMLDecodeError:
            return False
        return True

    @staticmethod
    def sniff(path: Path, head: bytes) -> MetaDescription:
        text = _decode(head) or ""
        truncated = len(head) >= HEAD_BYTES
        meta = _base_text_meta(path, "TomlSniffer", text, truncated)
        md = meta["metadata"]
        md["format"] = "toml"

        keys: list[str] = []
        # Only parse when tomllib is present; a truncated head may not parse, so
        # failure here is expected and simply leaves keys empty.
        if tomllib is not None:
            try:
                keys = list(tomllib.loads(text).keys())
            except (tomllib.TOMLDecodeError, ValueError):
                keys = []
        if keys:
            md["keys"] = keys

        if keys:
            meta["nl_summary"] = (
                f"A TOML file with keys: {', '.join(keys)} ({md.get('size', 'unknown size')})."
            )
        else:
            meta["nl_summary"] = f"A TOML file ({md.get('size', 'unknown size')})."
        return meta


class StructuredTextSniffer:
    name = "StructuredTextSniffer"

    @staticmethod
    def can_sniff(path: Path, head: bytes) -> bool:
        text = _decode(head)
        if text is None:
            return False
        return _detect_jsonl(text) is not None or _detect_format(text) is not None

    @staticmethod
    def sniff(path: Path, head: bytes) -> MetaDescription:
        text = _decode(head) or ""
        truncated = len(head) >= HEAD_BYTES
        meta = _base_text_meta(path, "StructuredTextSniffer", text, truncated)
        md = meta["metadata"]

        jsonl = _detect_jsonl(text)
        detected = jsonl or _detect_format(text)
        if detected:
            md.update(detected)

        meta["nl_summary"] = _structured_summary(md)
        return meta


# The plain-text fallback is registered at the lowest priority (below) so it
# only wins when nothing structured matched.
class PlainTextSniffer:
    name = "PlainTextSniffer"

    @staticmethod
    def can_sniff(path: Path, head: bytes) -> bool:
        return _decode(head) is not None

    @staticmethod
    def sniff(path: Path, head: bytes) -> MetaDescription:
        text = _decode(head) or ""
        truncated = len(head) >= HEAD_BYTES
        meta = _base_text_meta(path, "PlainTextSniffer", text, truncated)
        md = meta["metadata"]
        md["format"] = "text"
        preview = text[:200].replace("\n", " ").strip()
        md["preview"] = preview
        line_word = "line" if md["sampled_line_count"] == 1 else "lines"
        suffix = " (sample)" if truncated else ""
        meta["nl_summary"] = (
            f"A text file with {md['sampled_line_count']} {line_word}{suffix} "
            f"({md.get('size', 'unknown size')})."
        )
        return meta


# TomlSniffer is registered BEFORE StructuredTextSniffer: both sit at
# PRIORITY_TEXT and ties break by registration order, so a .toml file (which
# StructuredTextSniffer could misread) is claimed here first.
SnifferRegistry.register(TomlSniffer, priority=PRIORITY_TEXT)
SnifferRegistry.register(StructuredTextSniffer, priority=PRIORITY_TEXT)
SnifferRegistry.register(PlainTextSniffer, priority=PRIORITY_FALLBACK)


def _detect_jsonl(text: str) -> dict[str, Any] | None:
    """Detect newline-delimited JSON: several lines that each parse as JSON."""
    
    lines = [ln for ln in text.splitlines() if ln.strip()]
    if len(lines) < 2:
        return None
    # A single JSON object/array spanning lines is JSON, not JSONL.
    parseable = 0
    for line in lines[:20]:
        try:
            json.loads(line)
            parseable += 1
        except ValueError:
            return None
    if parseable < 2:
        return None
    return {"format": "jsonl", "sampled_records": parseable}


def _structured_summary(md: dict[str, Any]) -> str:
    fmt = md.get("format")
    size = md.get("size", "unknown size")
    if fmt == "jsonl":
        return (
            f"A JSON Lines file (~{md.get('sampled_records', '?')}+ records sampled) "
            f"({size})."
        )
    if fmt == "json":
        keys = md.get("keys")
        if keys:
            return f"A JSON file containing an object with keys: {', '.join(keys)} ({size})."
        return f"A JSON file ({size})."
    if fmt == "csv":
        cols = md.get("columns")
        header = md.get("header", [])
        head_str = f" Header: {', '.join(header)}." if header else ""
        return f"A CSV file with {cols} columns ({size}).{head_str}"
    if fmt == "yaml":
        keys = md.get("keys")
        if keys:
            return f"A YAML file with keys: {', '.join(keys)} ({size})."
        return f"A YAML file ({size})."
    if fmt == "xml":
        return f"An XML file with root <{md.get('root_tag')}> ({size})."
    if fmt == "html":
        return f"An HTML file ({size})."
    return f"A structured text file ({size})."
