"""Tests for primitive adapters."""

from pretty_little_summary.adapters import dispatch_adapter
from pretty_little_summary.synthesizer import deterministic_summary
from tests.input import build_input, expected_output, load_example


def test_int_special_year() -> None:
    example = load_example("int_special_year")
    meta = dispatch_adapter(build_input(example))
    assert meta["adapter_used"] == "PrimitiveAdapter"
    assert meta["metadata"]["type"] == "int"
    assert meta["metadata"]["special_form"]["type"] == "year"
    summary = deterministic_summary(meta)
    print("int:", summary)
    assert summary == expected_output(example, meta)


def test_float_probability_pattern() -> None:
    example = load_example("float_probability_pattern")
    meta = dispatch_adapter(build_input(example))
    assert meta["adapter_used"] == "PrimitiveAdapter"
    assert meta["metadata"]["type"] == "float"
    assert meta["metadata"]["pattern"] == "probability"
    summary = deterministic_summary(meta)
    print("float:", summary)
    assert summary == expected_output(example, meta)


def test_short_string_url_pattern() -> None:
    example = load_example("short_string_url_pattern")
    meta = dispatch_adapter(build_input(example))
    assert meta["metadata"]["type"] == "string"
    assert meta["metadata"]["pattern"] == "url"
    summary = deterministic_summary(meta)
    print("string_url:", summary)
    assert summary == expected_output(example, meta)


def test_long_string_markdown_document() -> None:
    example = load_example("long_string_markdown_document")
    meta = dispatch_adapter(build_input(example))
    assert meta["metadata"]["type"] == "string"
    assert meta["metadata"]["document_type"] == "markdown"
    summary = deterministic_summary(meta)
    print("string_md:", summary)
    assert summary == expected_output(example, meta)


def test_bytes_signature() -> None:
    example = load_example("bytes_signature")
    meta = dispatch_adapter(build_input(example))
    assert meta["metadata"]["type"] == "bytes"
    assert meta["metadata"]["format"] == "png"
    summary = deterministic_summary(meta)
    print("bytes:", summary)
    assert summary == expected_output(example, meta)


def test_complex_number() -> None:
    example = load_example("complex_number")
    meta = dispatch_adapter(build_input(example))
    assert meta["metadata"]["type"] == "complex"
    summary = deterministic_summary(meta)
    print("complex:", summary)
    assert summary == expected_output(example, meta)


def test_decimal_number() -> None:
    example = load_example("decimal_number")
    meta = dispatch_adapter(build_input(example))
    assert meta["metadata"]["type"] == "decimal"
    summary = deterministic_summary(meta)
    print("decimal:", summary)
    assert summary == expected_output(example, meta)


def test_fraction_number() -> None:
    example = load_example("fraction_number")
    meta = dispatch_adapter(build_input(example))
    assert meta["metadata"]["type"] == "fraction"
    summary = deterministic_summary(meta)
    print("fraction:", summary)
    assert summary == expected_output(example, meta)
