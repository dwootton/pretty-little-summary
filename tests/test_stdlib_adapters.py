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
    assert "ISO:" in summary


def test_date_adapter() -> None:
    obj = date(2024, 1, 1)
    meta = dispatch_adapter(obj)
    assert meta["metadata"]["type"] == "date"


def test_time_adapter() -> None:
    obj = time(14, 30, 0)
    meta = dispatch_adapter(obj)
    assert meta["metadata"]["type"] == "time"


def test_timedelta_adapter() -> None:
    obj = timedelta(days=2, hours=3)
    meta = dispatch_adapter(obj)
    assert meta["metadata"]["type"] == "timedelta"


def test_pathlib_adapter() -> None:
    obj = Path("README.md")
    meta = dispatch_adapter(obj)
    assert meta["adapter_used"] == "PathlibAdapter"
    summary = deterministic_summary(meta)
    assert "Path:" in summary


def test_purepath_adapter() -> None:
    obj = PurePath("foo/bar.txt")
    meta = dispatch_adapter(obj)
    assert meta["metadata"]["type"] == "path"


def test_uuid_adapter() -> None:
    obj = uuid.uuid4()
    meta = dispatch_adapter(obj)
    assert meta["metadata"]["type"] == "uuid"


def test_regex_pattern_adapter() -> None:
    pattern = re.compile(r"\\w+")
    meta = dispatch_adapter(pattern)
    assert meta["metadata"]["type"] == "regex_pattern"


def test_regex_match_adapter() -> None:
    match = re.search(r"\\d+", "abc123")
    assert match is not None
    meta = dispatch_adapter(match)
    assert meta["metadata"]["type"] == "regex_match"


def test_io_bytesio_adapter() -> None:
    buf = io.BytesIO(b"hello")
    meta = dispatch_adapter(buf)
    assert meta["metadata"]["type"] == "bytesio"


def test_io_stringio_adapter() -> None:
    buf = io.StringIO("hello")
    meta = dispatch_adapter(buf)
    assert meta["metadata"]["type"] == "stringio"


@dataclass
class Point:
    x: int
    y: int


def test_dataclass_adapter() -> None:
    obj = Point(1, 2)
    meta = dispatch_adapter(obj)
    assert meta["metadata"]["type"] == "dataclass"


class Color(Enum):
    RED = 1
    BLUE = 2


def test_enum_adapter() -> None:
    meta = dispatch_adapter(Color.RED)
    assert meta["metadata"]["type"] == "enum"


def test_function_adapter() -> None:
    def sample_fn(x: int) -> int:
        return x + 1

    meta = dispatch_adapter(sample_fn)
    assert meta["metadata"]["type"] == "function"

