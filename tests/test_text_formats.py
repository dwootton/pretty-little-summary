"""Tests for text format adapter."""

import pytest

from wut_is.adapters import dispatch_adapter
from wut_is.synthesizer import deterministic_summary


def test_json_string() -> None:
    text = '{"name": "alice", "age": 30}'
    meta = dispatch_adapter(text)
    assert meta["adapter_used"] == "TextFormatAdapter"
    assert meta["metadata"]["format"] == "json"
    summary = deterministic_summary(meta)
    print("json:", summary)
    assert "JSON string" in summary


def test_xml_string() -> None:
    text = "<root><child>value</child></root>"
    meta = dispatch_adapter(text)
    assert meta["metadata"]["format"] == "xml"
    summary = deterministic_summary(meta)
    print("xml:", summary)
    assert "XML document" in summary


def test_html_string() -> None:
    text = "<html><body><div>hello</div></body></html>"
    meta = dispatch_adapter(text)
    assert meta["metadata"]["format"] == "html"
    summary = deterministic_summary(meta)
    print("html:", summary)
    assert "HTML document" in summary


def test_csv_string() -> None:
    text = "a,b,c\n1,2,3\n4,5,6\n"
    meta = dispatch_adapter(text)
    assert meta["metadata"]["format"] == "csv"
    summary = deterministic_summary(meta)
    print("csv:", summary)
    assert "A CSV string" in summary
    assert "Best displayed as sortable table." in summary


def test_yaml_string() -> None:
    yaml = pytest.importorskip("yaml")
    text = "name: alice\nage: 30\n"
    meta = dispatch_adapter(text)
    assert meta["metadata"]["format"] == "yaml"
    summary = deterministic_summary(meta)
    print("yaml:", summary)
    assert "YAML string" in summary
