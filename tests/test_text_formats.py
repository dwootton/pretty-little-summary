"""Tests for text format adapter."""

import pytest

from pretty_little_summary.adapters import dispatch_adapter
from pretty_little_summary.synthesizer import deterministic_summary
from tests.input import build_input, expected_output, load_example


def test_json_string() -> None:
    example = load_example("json_string")
    meta = dispatch_adapter(build_input(example))
    assert meta["adapter_used"] == "TextFormatAdapter"
    assert meta["metadata"]["format"] == "json"
    summary = deterministic_summary(meta)
    print("json:", summary)
    assert summary == expected_output(example, meta)


def test_xml_string() -> None:
    example = load_example("xml_string")
    meta = dispatch_adapter(build_input(example))
    assert meta["metadata"]["format"] == "xml"
    summary = deterministic_summary(meta)
    print("xml:", summary)
    assert summary == expected_output(example, meta)


def test_html_string() -> None:
    example = load_example("html_string")
    meta = dispatch_adapter(build_input(example))
    assert meta["metadata"]["format"] == "html"
    summary = deterministic_summary(meta)
    print("html:", summary)
    assert summary == expected_output(example, meta)


def test_csv_string() -> None:
    example = load_example("csv_string")
    meta = dispatch_adapter(build_input(example))
    assert meta["metadata"]["format"] == "csv"
    summary = deterministic_summary(meta)
    print("csv:", summary)
    assert summary == expected_output(example, meta)


def test_yaml_string() -> None:
    yaml = pytest.importorskip("yaml")
    example = load_example("yaml_string")
    meta = dispatch_adapter(build_input(example))
    assert meta["metadata"]["format"] == "yaml"
    summary = deterministic_summary(meta)
    print("yaml:", summary)
    assert summary == expected_output(example, meta)
