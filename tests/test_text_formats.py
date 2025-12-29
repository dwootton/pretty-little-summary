"""Tests for text format adapter."""

import pytest

from pretty_little_summary.adapters import dispatch_adapter
from pretty_little_summary.synthesizer import deterministic_summary


def test_json_string() -> None:
    text = '{"name": "alice", "age": 30}'
    meta = dispatch_adapter(text)
    assert meta["adapter_used"] == "TextFormatAdapter"
    assert meta["metadata"]["format"] == "json"
    summary = deterministic_summary(meta)
    print("json:", summary)
    assert summary == "A valid JSON string containing an object with keys: name, age."


def test_xml_string() -> None:
    text = "<root><child>value</child></root>"
    meta = dispatch_adapter(text)
    assert meta["metadata"]["format"] == "xml"
    summary = deterministic_summary(meta)
    print("xml:", summary)
    assert summary == "A valid XML document with root <root>."


def test_html_string() -> None:
    text = "<html><body><div>hello</div></body></html>"
    meta = dispatch_adapter(text)
    assert meta["metadata"]["format"] == "html"
    summary = deterministic_summary(meta)
    print("html:", summary)
    assert summary == "An HTML document or fragment."


def test_csv_string() -> None:
    text = "a,b,c\n1,2,3\n4,5,6\n"
    meta = dispatch_adapter(text)
    assert meta["metadata"]["format"] == "csv"
    summary = deterministic_summary(meta)
    print("csv:", summary)
    assert summary == (
        "A CSV string with 3 rows and 3 columns (,-delimited). "
        "Header: 'a', 'b', 'c'. Sample: [\"'1'\", \"'2'\", \"'3'\"]. "
        "Column types: int, int, int. Best displayed as sortable table."
    )


def test_yaml_string() -> None:
    yaml = pytest.importorskip("yaml")
    text = "name: alice\nage: 30\n"
    meta = dispatch_adapter(text)
    assert meta["metadata"]["format"] == "yaml"
    summary = deterministic_summary(meta)
    print("yaml:", summary)
    assert summary == "A valid YAML string containing keys: name, age."
