"""Tests for stdlib adapters."""

from __future__ import annotations

from pathlib import Path

from pretty_little_summary.adapters import dispatch_adapter
from pretty_little_summary.synthesizer import deterministic_summary
from tests.input import build_input, expected_output, load_example


def test_datetime_adapter() -> None:
    example = load_example("datetime_adapter")
    meta = dispatch_adapter(build_input(example))
    assert meta["adapter_used"] == "DateTimeAdapter"
    summary = deterministic_summary(meta)
    print("datetime:", summary)
    assert summary == expected_output(example, meta)


def test_date_adapter() -> None:
    example = load_example("date_adapter")
    meta = dispatch_adapter(build_input(example))
    assert meta["metadata"]["type"] == "date"
    summary = deterministic_summary(meta)
    print("date:", summary)
    assert summary == expected_output(example, meta)


def test_time_adapter() -> None:
    example = load_example("time_adapter")
    meta = dispatch_adapter(build_input(example))
    assert meta["metadata"]["type"] == "time"
    summary = deterministic_summary(meta)
    print("time:", summary)
    assert summary == expected_output(example, meta)


def test_timedelta_adapter() -> None:
    example = load_example("timedelta_adapter")
    meta = dispatch_adapter(build_input(example))
    assert meta["metadata"]["type"] == "timedelta"
    summary = deterministic_summary(meta)
    print("timedelta:", summary)
    assert summary == expected_output(example, meta)


def test_pathlib_adapter(tmp_path: Path) -> None:
    example = load_example("pathlib_adapter")
    meta = dispatch_adapter(build_input(example, tmp_path=tmp_path))
    assert meta["adapter_used"] == "PathlibAdapter"
    summary = deterministic_summary(meta)
    print("path:", summary)
    assert summary == expected_output(example, meta)


def test_purepath_adapter() -> None:
    example = load_example("purepath_adapter")
    meta = dispatch_adapter(build_input(example))
    assert meta["metadata"]["type"] == "path"
    summary = deterministic_summary(meta)
    print("purepath:", summary)
    assert summary == expected_output(example, meta)


def test_uuid_adapter() -> None:
    example = load_example("uuid_adapter")
    meta = dispatch_adapter(build_input(example))
    assert meta["metadata"]["type"] == "uuid"
    print("uuid:", deterministic_summary(meta))
    assert deterministic_summary(meta) == expected_output(example, meta)


def test_regex_pattern_adapter() -> None:
    example = load_example("regex_pattern_adapter")
    meta = dispatch_adapter(build_input(example))
    assert meta["metadata"]["type"] == "regex_pattern"
    summary = deterministic_summary(meta)
    print("regex_pattern:", summary)
    assert summary == expected_output(example, meta)


def test_regex_match_adapter() -> None:
    example = load_example("regex_match_adapter")
    meta = dispatch_adapter(build_input(example))
    assert meta["metadata"]["type"] == "regex_match"
    summary = deterministic_summary(meta)
    print("regex_match:", summary)
    assert summary == expected_output(example, meta)


def test_traceback_adapter() -> None:
    example = load_example("traceback_adapter")
    meta = dispatch_adapter(build_input(example))
    summary = deterministic_summary(meta)
    print("traceback:", summary)
    assert summary == expected_output(example, meta)


def test_io_bytesio_adapter() -> None:
    example = load_example("io_bytesio_adapter")
    meta = dispatch_adapter(build_input(example))
    assert meta["metadata"]["type"] == "bytesio"
    summary = deterministic_summary(meta)
    print("bytesio:", summary)
    assert summary == expected_output(example, meta)


def test_io_stringio_adapter() -> None:
    example = load_example("io_stringio_adapter")
    meta = dispatch_adapter(build_input(example))
    assert meta["metadata"]["type"] == "stringio"
    summary = deterministic_summary(meta)
    print("stringio:", summary)
    assert summary == expected_output(example, meta)


def test_dataclass_adapter() -> None:
    example = load_example("dataclass_adapter")
    meta = dispatch_adapter(build_input(example))
    assert meta["metadata"]["type"] == "dataclass"
    summary = deterministic_summary(meta)
    print("dataclass:", summary)
    assert summary == expected_output(example, meta)


def test_enum_adapter() -> None:
    example = load_example("enum_adapter")
    meta = dispatch_adapter(build_input(example))
    assert meta["metadata"]["type"] == "enum"
    summary = deterministic_summary(meta)
    print("enum:", summary)
    assert summary == expected_output(example, meta)


def test_function_adapter() -> None:
    example = load_example("function_adapter")
    meta = dispatch_adapter(build_input(example))
    assert meta["metadata"]["type"] == "function"
    summary = deterministic_summary(meta)
    print("function:", summary)
    assert summary == expected_output(example, meta)
