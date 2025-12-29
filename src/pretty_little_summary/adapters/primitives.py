"""Adapter for core Python primitives (int, float, bool, None, str, bytes)."""

from __future__ import annotations

from collections import Counter
from datetime import datetime
from decimal import Decimal
from fractions import Fraction
import cmath
import json
import math
import re
from typing import Any

from pretty_little_summary.adapters._base import AdapterRegistry
from pretty_little_summary.descriptor_registry import DescribeConfigRegistry
from pretty_little_summary.descriptor_utils import format_bytes, safe_repr
from pretty_little_summary.core import MetaDescription


class PrimitiveAdapter:
    """Adapter for primitive built-in types."""

    @staticmethod
    def can_handle(obj: Any) -> bool:
        if type(obj).__module__.startswith("numpy"):
            return False
        return isinstance(
            obj,
            (bool, int, float, complex, Decimal, Fraction, str, bytes, bytearray, type(None)),
        )

    @staticmethod
    def extract_metadata(obj: Any) -> MetaDescription:
        config = DescribeConfigRegistry.get()
        meta: MetaDescription = {
            "object_type": f"{type(obj).__module__}.{type(obj).__name__}",
            "adapter_used": "PrimitiveAdapter",
        }

        metadata: dict[str, Any] = {}

        if obj is None:
            metadata["type"] = "none"
            metadata["value"] = None
        elif isinstance(obj, bool):
            metadata["type"] = "bool"
            metadata["value"] = bool(obj)
        elif isinstance(obj, int):
            metadata.update(_describe_int(obj))
        elif isinstance(obj, float):
            metadata.update(_describe_float(obj))
        elif isinstance(obj, complex):
            metadata.update(_describe_complex(obj))
        elif isinstance(obj, Decimal):
            metadata.update(_describe_decimal(obj))
        elif isinstance(obj, Fraction):
            metadata.update(_describe_fraction(obj))
        elif isinstance(obj, str):
            if len(obj) < 100:
                metadata.update(_describe_short_string(obj, config.max_string_preview))
            else:
                metadata.update(_describe_long_string(obj, config.max_string_preview))
        elif isinstance(obj, (bytes, bytearray)):
            metadata.update(_describe_bytes(obj))
        else:
            metadata["value"] = safe_repr(obj, config.max_sample_repr)

        if metadata:
            meta["metadata"] = metadata
            meta["nl_summary"] = _build_nl_summary(metadata)

        return meta


def _describe_int(value: int) -> dict[str, Any]:
    magnitude = "small" if abs(value) < 100 else "medium" if abs(value) < 1_000_000 else "large"
    sign = "zero" if value == 0 else "positive" if value > 0 else "negative"
    special = _detect_int_special(value)
    metadata: dict[str, Any] = {
        "type": "int",
        "value": value,
        "magnitude": magnitude,
        "sign": sign,
    }
    if special:
        metadata["special_form"] = special
    if special and special.get("type") == "bit_flag":
        metadata["hex"] = hex(value)
    return metadata


def _detect_int_special(value: int) -> dict[str, Any] | None:
    if value == 0:
        return None
    if value > 0 and (value & (value - 1) == 0):
        return {"type": "bit_flag", "bit": int(math.log2(value))}
    if 1900 <= value <= 2100:
        return {"type": "year", "value": value}
    if 100 <= value <= 599:
        return {"type": "http_status", "value": value}
    if 0 <= value <= 255:
        return {"type": "exit_code", "value": value}
    if 0 <= value <= 65535:
        return {"type": "port_number", "value": value}
    if value >= 1_000_000_000:
        try:
            dt = datetime.utcfromtimestamp(value)
            return {"type": "timestamp_unix", "utc": dt.isoformat() + "Z"}
        except (OverflowError, OSError, ValueError):
            return {"type": "timestamp_unix", "value": value}
    return None


def _describe_float(value: float) -> dict[str, Any]:
    metadata: dict[str, Any] = {"type": "float"}
    if math.isnan(value):
        metadata["special"] = "nan"
        metadata["value"] = "NaN"
        return metadata
    if math.isinf(value):
        metadata["special"] = "inf" if value > 0 else "-inf"
        metadata["value"] = "Infinity" if value > 0 else "-Infinity"
        return metadata

    metadata["value"] = value
    precision = _float_precision(value)
    if precision is not None:
        metadata["precision"] = precision
    pattern = _detect_float_pattern(value)
    if pattern:
        metadata["pattern"] = pattern
    return metadata


def _describe_complex(value: complex) -> dict[str, Any]:
    magnitude = abs(value)
    phase = math.degrees(cmath.phase(value))
    return {
        "type": "complex",
        "real": value.real,
        "imag": value.imag,
        "magnitude": magnitude,
        "phase_degrees": round(phase, 2),
    }


def _describe_decimal(value: Decimal) -> dict[str, Any]:
    if value.is_nan():
        special = "nan"
    elif value.is_infinite():
        special = "infinite"
    else:
        special = None
    sign, digits, exponent = value.as_tuple()
    precision = len(digits)
    return {
        "type": "decimal",
        "value": str(value),
        "sign": "-" if sign else "+",
        "precision": precision,
        "exponent": exponent,
        "special": special,
    }


def _describe_fraction(value: Fraction) -> dict[str, Any]:
    return {
        "type": "fraction",
        "numerator": value.numerator,
        "denominator": value.denominator,
        "float_value": float(value),
        "is_integer": value.denominator == 1,
    }


def _build_nl_summary(metadata: dict[str, Any]) -> str:
    ptype = metadata.get("type")
    if ptype == "int":
        value = metadata.get("value")
        special = metadata.get("special_form")
        if special:
            return f"The integer {value}, likely a {special.get('type')}."
        return f"An integer with value {value}."
    if ptype == "float":
        value = metadata.get("value")
        pattern = metadata.get("pattern")
        if pattern:
            return f"A float {value}, likely representing a {pattern}."
        return f"A floating-point number with value {value}."
    if ptype == "bool":
        return f"A boolean value: {metadata.get('value')}."
    if ptype == "none":
        return "A None value (null or missing)."
    if ptype == "string":
        if metadata.get("document_type"):
            return f"A {metadata.get('document_type')} document string ({metadata.get('length')} chars)."
        pattern = metadata.get("pattern")
        if pattern:
            return f"A string containing a {pattern}: '{metadata.get('value')}'."
        return f"A string '{metadata.get('value')}' ({metadata.get('length')} characters)."
    if ptype == "bytes":
        fmt = metadata.get("format")
        if fmt:
            return f"A bytes object containing {fmt} data ({metadata.get('length')} bytes)."
        return f"A bytes object of {metadata.get('length')} bytes."
    if ptype == "complex":
        return f"A complex number {metadata.get('real')} + {metadata.get('imag')}i."
    if ptype == "decimal":
        return (
            f"A Decimal value {metadata.get('value')} with {metadata.get('precision')} digits of precision."
        )
    if ptype == "fraction":
        return f"A Fraction {metadata.get('numerator')}/{metadata.get('denominator')}."
    return f"A {ptype} value."


def _float_precision(value: float) -> int | None:
    text = repr(value)
    if "e" in text or "E" in text:
        base = text.split("e")[0]
    else:
        base = text
    digits = [c for c in base if c.isdigit()]
    return len(digits) if digits else None


def _detect_float_pattern(value: float) -> str | None:
    if 0 <= value <= 1:
        return "probability"
    if 0 <= value <= 100:
        return "percentage"
    if -90 <= value <= 90:
        return "latitude"
    if -180 <= value <= 180:
        return "longitude"
    if abs(value) < 1_000_000 and round(value, 2) == value:
        return "currency_like"
    return None


def _describe_short_string(value: str, max_preview: int) -> dict[str, Any]:
    metadata: dict[str, Any] = {
        "type": "string",
        "length": len(value),
        "value": value[:max_preview],
    }
    pattern = _detect_short_string_pattern(value)
    if pattern:
        metadata["pattern"] = pattern
    metadata["charset"] = _string_charset(value)
    content_type = _string_content_type(value)
    if content_type:
        metadata["content_type"] = content_type
    return metadata


def _describe_long_string(value: str, max_preview: int) -> dict[str, Any]:
    preview = value[:max_preview]
    tail = value[-max_preview:] if len(value) > max_preview else ""
    line_count = value.count("\n") + 1
    word_count = len(value.split())
    doc_type = _detect_document_type(value)

    return {
        "type": "string",
        "length": len(value),
        "preview": preview,
        "tail_preview": tail if tail else None,
        "line_count": line_count,
        "word_count": word_count,
        "document_type": doc_type,
        "charset": _string_charset(value),
    }


def _string_charset(value: str) -> str:
    if all(ord(c) < 128 for c in value):
        return "ascii"
    if any(_is_emoji(c) for c in value):
        return "unicode_with_emoji"
    return "unicode"


def _is_emoji(char: str) -> bool:
    return ord(char) > 0x1F000


def _string_content_type(value: str) -> str | None:
    if value.isidentifier():
        return "identifier"
    if " " in value:
        return "sentence" if value.endswith((".", "!", "?")) else "phrase"
    if value.isalnum():
        return "alphanumeric"
    return None


def _detect_short_string_pattern(value: str) -> str | None:
    if _is_url(value):
        return "url"
    if _is_email(value):
        return "email"
    if _is_iso_date(value):
        return "iso_date"
    if _is_iso_datetime(value):
        return "iso_datetime"
    if _is_uuid(value):
        return "uuid"
    if _is_file_path(value):
        return "file_path"
    if _is_phone(value):
        return "phone"
    if _is_hex_color(value):
        return "hex_color"
    if _is_ip_address(value):
        return "ip_address"
    if _looks_like_json(value):
        return "json"
    return None


def _detect_document_type(value: str) -> str | None:
    stripped = value.lstrip()
    if stripped.startswith(("{", "[")) and _is_valid_json(stripped):
        return "json"
    if stripped.startswith("<") and ("</" in value or "<html" in value.lower()):
        return "html_or_xml"
    if _looks_like_markdown(value):
        return "markdown"
    if _looks_like_python(value):
        return "python_code"
    if _looks_like_sql(value):
        return "sql"
    if _looks_like_csv(value):
        return "csv"
    return "prose"


def _describe_bytes(obj: bytes | bytearray) -> dict[str, Any]:
    data = bytes(obj)
    length = len(data)
    preview_hex = data[:20].hex()
    detected = _detect_magic_bytes(data)
    entropy = _entropy(data) if data else 0.0

    metadata: dict[str, Any] = {
        "type": "bytes",
        "length": length,
        "size": format_bytes(length),
        "preview_hex": preview_hex,
        "entropy": round(entropy, 2),
    }
    if isinstance(obj, bytearray):
        metadata["mutable"] = True
    if detected:
        metadata["format"] = detected
    if _is_valid_utf8(data):
        metadata["utf8"] = True
    return metadata


def _detect_magic_bytes(data: bytes) -> str | None:
    signatures = {
        b"\x89PNG\r\n\x1a\n": "png",
        b"\xff\xd8\xff": "jpeg",
        b"GIF87a": "gif",
        b"GIF89a": "gif",
        b"%PDF": "pdf",
        b"PK\x03\x04": "zip",
        b"\x1f\x8b": "gzip",
        b"SQLite format 3\x00": "sqlite",
    }
    for sig, name in signatures.items():
        if data.startswith(sig):
            return name
    return None


def _entropy(data: bytes) -> float:
    counts = Counter(data)
    total = len(data)
    if total == 0:
        return 0.0
    return -sum((count / total) * math.log2(count / total) for count in counts.values())


def _is_valid_utf8(data: bytes) -> bool:
    try:
        data.decode("utf-8")
        return True
    except UnicodeDecodeError:
        return False


def _is_valid_json(value: str) -> bool:
    try:
        json.loads(value)
        return True
    except (ValueError, json.JSONDecodeError):
        return False


def _looks_like_json(value: str) -> bool:
    value = value.strip()
    if not value.startswith(("{", "[")):
        return False
    return _is_valid_json(value)


def _is_url(value: str) -> bool:
    return bool(re.match(r"^https?://[^\s<>]+$", value))


def _is_email(value: str) -> bool:
    return bool(re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", value))


def _is_iso_date(value: str) -> bool:
    return bool(re.match(r"^\d{4}-\d{2}-\d{2}$", value))


def _is_iso_datetime(value: str) -> bool:
    return bool(re.match(r"^\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}", value))


def _is_uuid(value: str) -> bool:
    return bool(
        re.match(
            r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
            value,
            re.I,
        )
    )


def _is_file_path(value: str) -> bool:
    unix = re.match(r"^(/[^/\0]+)+/?$", value)
    windows = re.match(
        r"^[A-Za-z]:\\(?:[^\\/:*?\"<>|\r\n]+\\)*[^\\/:*?\"<>|\r\n]*$",
        value,
    )
    return bool(unix or windows)


def _is_phone(value: str) -> bool:
    return bool(
        re.match(
            r"\b(\+?1?[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b",
            value,
        )
    )


def _is_hex_color(value: str) -> bool:
    return bool(re.match(r"^#(?:[0-9a-fA-F]{3}){1,2}$", value))


def _is_ip_address(value: str) -> bool:
    return bool(re.match(r"^\d{1,3}(\.\d{1,3}){3}$", value))


def _looks_like_markdown(value: str) -> bool:
    return value.lstrip().startswith("#") or "```" in value


def _looks_like_python(value: str) -> bool:
    return "def " in value or "import " in value or "class " in value


def _looks_like_sql(value: str) -> bool:
    upper = value.upper()
    return "SELECT " in upper and " FROM " in upper


def _looks_like_csv(value: str) -> bool:
    lines = [line for line in value.splitlines() if line.strip()]
    if len(lines) < 2:
        return False
    counts = [line.count(",") for line in lines[:5]]
    return len(set(counts)) == 1 and counts[0] > 0


# Auto-register adapter
AdapterRegistry.register(PrimitiveAdapter)
