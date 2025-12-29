"""Adapter for serialized text formats (JSON/YAML/XML/HTML/CSV)."""

from __future__ import annotations

import csv
import json
import re
import xml.etree.ElementTree as ET
from typing import Any

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False

from pretty_little_summary.adapters._base import AdapterRegistry
from pretty_little_summary.core import MetaDescription
from pretty_little_summary.descriptor_utils import safe_repr


class TextFormatAdapter:
    """Adapter for strings that represent structured data formats."""

    @staticmethod
    def can_handle(obj: Any) -> bool:
        if not isinstance(obj, str):
            return False
        return _detect_format(obj) is not None

    @staticmethod
    def extract_metadata(obj: Any) -> MetaDescription:
        meta: MetaDescription = {
            "object_type": "builtins.str",
            "adapter_used": "TextFormatAdapter",
        }
        metadata: dict[str, Any] = {"type": "string", "length": len(obj)}

        detected = _detect_format(obj)
        if detected:
            metadata.update(detected)

        meta["metadata"] = metadata
        meta["nl_summary"] = _build_nl_summary(metadata)
        return meta


def _detect_format(value: str) -> dict[str, Any] | None:
    stripped = value.strip()
    if not stripped:
        return None

    json_meta = _detect_json(stripped)
    if json_meta:
        return json_meta

    if YAML_AVAILABLE:
        yaml_meta = _detect_yaml(stripped)
        if yaml_meta:
            return yaml_meta

    html_meta = _detect_html(stripped)
    if html_meta:
        return html_meta

    xml_meta = _detect_xml(stripped)
    if xml_meta:
        return xml_meta

    csv_meta = _detect_csv(value)
    if csv_meta:
        return csv_meta

    return None


def _detect_json(value: str) -> dict[str, Any] | None:
    if not value.startswith(("{", "[")):
        return None
    try:
        parsed = json.loads(value)
    except (ValueError, json.JSONDecodeError):
        return None
    meta: dict[str, Any] = {"format": "json", "parsed_type": type(parsed).__name__}
    if isinstance(parsed, dict):
        meta["keys"] = list(parsed.keys())[:10]
    elif isinstance(parsed, list):
        meta["length"] = len(parsed)
    return meta


def _detect_yaml(value: str) -> dict[str, Any] | None:
    if not YAML_AVAILABLE:
        return None
    if not (value.startswith("---") or re.search(r"^\w+:\s", value, re.M)):
        return None
    try:
        parsed = yaml.safe_load(value)
    except Exception:
        return None
    meta: dict[str, Any] = {"format": "yaml", "parsed_type": type(parsed).__name__}
    if isinstance(parsed, dict):
        meta["keys"] = list(parsed.keys())[:10]
    return meta


def _detect_xml(value: str) -> dict[str, Any] | None:
    if not value.startswith("<"):
        return None
    try:
        root = ET.fromstring(value)
    except Exception:
        return None
    return {"format": "xml", "root_tag": root.tag}


def _detect_html(value: str) -> dict[str, Any] | None:
    if not re.search(r"<!doctype\s+html|<html\b|<body\b|<head\b", value, re.I):
        if not re.search(r"<(div|span|p|a|img|table|section)\b", value, re.I):
            return None
    return {"format": "html"}


def _detect_csv(value: str) -> dict[str, Any] | None:
    lines = [line for line in value.splitlines() if line.strip()]
    if len(lines) < 2:
        return None
    sample = "\n".join(lines[:5])
    try:
        dialect = csv.Sniffer().sniff(sample)
    except Exception:
        return None
    reader = csv.reader(lines[:5], dialect)
    rows = list(reader)
    if len(rows) < 2:
        return None
    header = rows[0]
    sample_rows = rows[:3]
    col_types = _infer_column_types(sample_rows[1:]) if len(sample_rows) > 1 else []
    return {
        "format": "csv",
        "delimiter": dialect.delimiter,
        "rows": len(lines),
        "columns": len(header),
        "header": [safe_repr(h, 50) for h in header],
        "sample_row": [safe_repr(cell, 50) for cell in (sample_rows[1] if len(sample_rows) > 1 else [])],
        "column_types": col_types,
    }


def _infer_column_types(rows: list[list[str]]) -> list[str]:
    if not rows:
        return []
    n_cols = max(len(row) for row in rows)
    types = []
    for col in range(n_cols):
        values = [row[col] for row in rows if len(row) > col]
        types.append(_infer_type(values))
    return types


def _infer_type(values: list[str]) -> str:
    if all(_is_int(v) for v in values):
        return "int"
    if all(_is_float(v) for v in values):
        return "float"
    if all(_is_date(v) for v in values):
        return "date"
    if all(_is_email(v) for v in values):
        return "email"
    if all(_is_bool(v) for v in values):
        return "bool"
    return "str"


def _is_int(value: str) -> bool:
    return re.fullmatch(r"-?\d+", value or "") is not None


def _is_float(value: str) -> bool:
    return re.fullmatch(r"-?\d+\.\d+", value or "") is not None


def _is_date(value: str) -> bool:
    return re.fullmatch(r"\d{4}-\d{2}-\d{2}", value or "") is not None


def _is_email(value: str) -> bool:
    return re.fullmatch(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", value or "") is not None


def _is_bool(value: str) -> bool:
    return value.lower() in {"true", "false"}


AdapterRegistry.register(TextFormatAdapter)


def _build_nl_summary(metadata: dict[str, Any]) -> str:
    fmt = metadata.get("format")
    if fmt == "csv":
        rows = metadata.get("rows")
        cols = metadata.get("columns")
        delimiter = metadata.get("delimiter")
        header = metadata.get("header", [])
        sample = metadata.get("sample_row", [])
        col_types = metadata.get("column_types", [])
        parts = [
            f"A CSV string with {rows} rows and {cols} columns ({delimiter}-delimited)."
        ]
        if header:
            parts.append(f"Header: {', '.join(header)}.")
        if sample:
            parts.append(f"Sample: {sample}.")
        if col_types:
            parts.append(f"Column types: {', '.join(col_types)}.")
        parts.append("Best displayed as sortable table.")
        return " ".join(parts)
    if fmt == "json":
        keys = metadata.get("keys")
        if keys:
            return f"A valid JSON string containing an object with keys: {', '.join(keys)}."
        return "A valid JSON string."
    if fmt == "yaml":
        keys = metadata.get("keys")
        if keys:
            return f"A valid YAML string containing keys: {', '.join(keys)}."
        return "A valid YAML string."
    if fmt == "xml":
        root = metadata.get("root_tag")
        return f"A valid XML document with root <{root}>."
    if fmt == "html":
        return "An HTML document or fragment."
    return "A structured text string."
