"""Tests for primitive adapters."""

from pretty_little_summary.adapters import dispatch_adapter
from pretty_little_summary.synthesizer import deterministic_summary
from decimal import Decimal
from fractions import Fraction


def test_int_special_year() -> None:
    meta = dispatch_adapter(2020)
    assert meta["adapter_used"] == "PrimitiveAdapter"
    assert meta["metadata"]["type"] == "int"
    assert meta["metadata"]["special_form"]["type"] == "year"
    summary = deterministic_summary(meta)
    print("int:", summary)
    assert summary == "The integer 2020, likely a year."


def test_float_probability_pattern() -> None:
    meta = dispatch_adapter(0.5)
    assert meta["adapter_used"] == "PrimitiveAdapter"
    assert meta["metadata"]["type"] == "float"
    assert meta["metadata"]["pattern"] == "probability"
    summary = deterministic_summary(meta)
    print("float:", summary)
    assert summary == "A float 0.5, likely representing a probability."


def test_short_string_url_pattern() -> None:
    meta = dispatch_adapter("https://example.com/foo")
    assert meta["metadata"]["type"] == "string"
    assert meta["metadata"]["pattern"] == "url"
    summary = deterministic_summary(meta)
    print("string_url:", summary)
    assert summary == "A string containing a url: 'https://example.com/foo'."


def test_long_string_markdown_document() -> None:
    text = "# Title\n\nThis is a paragraph.\n\n```python\nprint('hi')\n```\n"
    text = text * 10
    meta = dispatch_adapter(text)
    assert meta["metadata"]["type"] == "string"
    assert meta["metadata"]["document_type"] == "markdown"
    summary = deterministic_summary(meta)
    print("string_md:", summary)
    assert summary == "A markdown document string (570 chars)."


def test_bytes_signature() -> None:
    png_header = b"\x89PNG\r\n\x1a\n" + b"\x00" * 20
    meta = dispatch_adapter(png_header)
    assert meta["metadata"]["type"] == "bytes"
    assert meta["metadata"]["format"] == "png"
    summary = deterministic_summary(meta)
    print("bytes:", summary)
    assert summary == "A bytes object containing png data (28 bytes)."


def test_complex_number() -> None:
    meta = dispatch_adapter(3 + 4j)
    assert meta["metadata"]["type"] == "complex"
    summary = deterministic_summary(meta)
    print("complex:", summary)
    assert summary == "A complex number 3.0 + 4.0i."


def test_decimal_number() -> None:
    meta = dispatch_adapter(Decimal("12.34"))
    assert meta["metadata"]["type"] == "decimal"
    summary = deterministic_summary(meta)
    print("decimal:", summary)
    assert summary == "A Decimal value 12.34 with 4 digits of precision."


def test_fraction_number() -> None:
    meta = dispatch_adapter(Fraction(1, 3))
    assert meta["metadata"]["type"] == "fraction"
    summary = deterministic_summary(meta)
    print("fraction:", summary)
    assert summary == "A Fraction 1/3."
