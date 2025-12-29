"""Tests for stdlib adapters."""

from __future__ import annotations

import io
import re
import uuid
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from enum import Enum
from pathlib import Path, PurePath

from wut_is.adapters import dispatch_adapter
from wut_is.synthesizer import deterministic_summary


def test_datetime_adapter() -> None:
    obj = datetime(2024, 1, 1, 12, 0, 0)
    meta = dispatch_adapter(obj)
    assert meta["adapter_used"] == "DateTimeAdapter"
    summary = deterministic_summary(meta)
    print("datetime:", summary)
    assert "datetime value" in summary


def test_date_adapter() -> None:
    obj = date(2024, 1, 1)
    meta = dispatch_adapter(obj)
    assert meta["metadata"]["type"] == "date"
    print("date:", deterministic_summary(meta))
    assert "date value" in deterministic_summary(meta)


def test_time_adapter() -> None:
    obj = time(14, 30, 0)
    meta = dispatch_adapter(obj)
    assert meta["metadata"]["type"] == "time"
    print("time:", deterministic_summary(meta))
    assert "time value" in deterministic_summary(meta)


def test_timedelta_adapter() -> None:
    obj = timedelta(days=2, hours=3)
    meta = dispatch_adapter(obj)
    assert meta["metadata"]["type"] == "timedelta"
    print("timedelta:", deterministic_summary(meta))
    assert "timedelta value" in deterministic_summary(meta)


def test_pathlib_adapter() -> None:
    obj = Path("README.md")
    meta = dispatch_adapter(obj)
    assert meta["adapter_used"] == "PathlibAdapter"
    summary = deterministic_summary(meta)
    print("path:", summary)
    assert "path 'README.md'" in summary


def test_purepath_adapter() -> None:
    obj = PurePath("foo/bar.txt")
    meta = dispatch_adapter(obj)
    assert meta["metadata"]["type"] == "path"
    print("purepath:", deterministic_summary(meta))
    assert "path 'foo/bar.txt'" in deterministic_summary(meta)


def test_uuid_adapter() -> None:
    obj = uuid.uuid4()
    meta = dispatch_adapter(obj)
    assert meta["metadata"]["type"] == "uuid"
    print("uuid:", deterministic_summary(meta))
    assert "UUID" in deterministic_summary(meta)


def test_regex_pattern_adapter() -> None:
    pattern = re.compile(r"\\w+")
    meta = dispatch_adapter(pattern)
    assert meta["metadata"]["type"] == "regex_pattern"
    print("regex_pattern:", deterministic_summary(meta))
    assert "regex" in deterministic_summary(meta)


def test_regex_match_adapter() -> None:
    match = re.search(r"\d+", "abc123")
    assert match is not None
    meta = dispatch_adapter(match)
    assert meta["metadata"]["type"] == "regex_match"
    print("regex_match:", deterministic_summary(meta))
    assert "regex" in deterministic_summary(meta)


def test_traceback_adapter() -> None:
    try:
        raise ValueError("boom")
    except ValueError as exc:
        tb_obj = exc.__traceback__
        assert tb_obj is not None
        meta = dispatch_adapter(tb_obj)
        summary = deterministic_summary(meta)
        print("traceback:", summary)
        assert "A traceback with" in summary


def test_io_bytesio_adapter() -> None:
    buf = io.BytesIO(b"hello")
    meta = dispatch_adapter(buf)
    assert meta["metadata"]["type"] == "bytesio"
    print("bytesio:", deterministic_summary(meta))
    assert "IO object" in deterministic_summary(meta)


def test_io_stringio_adapter() -> None:
    buf = io.StringIO("hello")
    meta = dispatch_adapter(buf)
    assert meta["metadata"]["type"] == "stringio"
    print("stringio:", deterministic_summary(meta))
    assert "IO object" in deterministic_summary(meta)


@dataclass
class Point:
    x: int
    y: int


def test_dataclass_adapter() -> None:
    obj = Point(1, 2)
    meta = dispatch_adapter(obj)
    assert meta["metadata"]["type"] == "dataclass"
    print("dataclass:", deterministic_summary(meta))
    assert "structured object" in deterministic_summary(meta)


class Color(Enum):
    RED = 1
    BLUE = 2


def test_enum_adapter() -> None:
    meta = dispatch_adapter(Color.RED)
    assert meta["metadata"]["type"] == "enum"
    print("enum:", deterministic_summary(meta))
    assert "structured object" in deterministic_summary(meta)


def test_function_adapter() -> None:
    def sample_fn(x: int) -> int:
        return x + 1

    meta = dispatch_adapter(sample_fn)
    assert meta["metadata"]["type"] == "function"
    print("function:", deterministic_summary(meta))
    assert "callable function" in deterministic_summary(meta)
