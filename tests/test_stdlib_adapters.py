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
    assert summary == "A datetime: 2024-01-01T12:00:00. Timezone: naive. Monday."


def test_date_adapter() -> None:
    obj = date(2024, 1, 1)
    meta = dispatch_adapter(obj)
    assert meta["metadata"]["type"] == "date"
    summary = deterministic_summary(meta)
    print("date:", summary)
    assert summary == "A date: 2024-01-01. Monday."


def test_time_adapter() -> None:
    obj = time(14, 30, 0)
    meta = dispatch_adapter(obj)
    assert meta["metadata"]["type"] == "time"
    summary = deterministic_summary(meta)
    print("time:", summary)
    assert summary == "A time: 14:30:00. Timezone: naive."


def test_timedelta_adapter() -> None:
    obj = timedelta(days=2, hours=3)
    meta = dispatch_adapter(obj)
    assert meta["metadata"]["type"] == "timedelta"
    summary = deterministic_summary(meta)
    print("timedelta:", summary)
    assert summary == "A duration of 2 days (183600 seconds)."


def test_pathlib_adapter(tmp_path: Path) -> None:
    target = tmp_path / "sample.txt"
    target.write_text("hello")
    obj = Path(target)
    meta = dispatch_adapter(obj)
    assert meta["adapter_used"] == "PathlibAdapter"
    summary = deterministic_summary(meta)
    print("path:", summary)
    assert summary == f"A path '{target}' pointing to an existing file (5.0 B)."


def test_purepath_adapter() -> None:
    obj = PurePath("foo/bar.txt")
    meta = dispatch_adapter(obj)
    assert meta["metadata"]["type"] == "path"
    summary = deterministic_summary(meta)
    print("purepath:", summary)
    assert summary == "A pure path 'foo/bar.txt'."


def test_uuid_adapter() -> None:
    obj = uuid.UUID("fd2559fe-4d56-4dd3-893c-2650a015551c")
    meta = dispatch_adapter(obj)
    assert meta["metadata"]["type"] == "uuid"
    print("uuid:", deterministic_summary(meta))
    assert deterministic_summary(meta) == (
        "A UUID (version 4): fd2559fe-4d56-4dd3-893c-2650a015551c."
    )


def test_regex_pattern_adapter() -> None:
    pattern = re.compile(r"\\w+")
    meta = dispatch_adapter(pattern)
    assert meta["metadata"]["type"] == "regex_pattern"
    summary = deterministic_summary(meta)
    print("regex_pattern:", summary)
    assert summary == "A compiled regex pattern /\\\\w+/."


def test_regex_match_adapter() -> None:
    match = re.search(r"\d+", "abc123")
    assert match is not None
    meta = dispatch_adapter(match)
    assert meta["metadata"]["type"] == "regex_match"
    summary = deterministic_summary(meta)
    print("regex_match:", summary)
    assert summary == "A regex match result: matched '123' at position 3:6."


def test_traceback_adapter() -> None:
    try:
        raise ValueError("boom")
    except ValueError as exc:
        tb_obj = exc.__traceback__
        assert tb_obj is not None
        meta = dispatch_adapter(tb_obj)
        summary = deterministic_summary(meta)
        print("traceback:", summary)
        frames = meta["metadata"]["frames"]
        expected_parts = [
            f"A traceback with {meta['metadata']['depth']} frames (most recent last):"
        ]
        for frame in frames:
            expected_parts.append(
                f"→ {frame.get('filename')}:{frame.get('line')} in {frame.get('name')}()"
            )
        last = meta["metadata"].get("last_frame")
        if last and last.get("code"):
            expected_parts.append(f"Last frame context: '{last.get('code')}'.")
        assert summary == "\n".join(expected_parts)


def test_io_bytesio_adapter() -> None:
    buf = io.BytesIO(b"hello")
    meta = dispatch_adapter(buf)
    assert meta["metadata"]["type"] == "bytesio"
    summary = deterministic_summary(meta)
    print("bytesio:", summary)
    assert summary == "An in-memory bytes buffer of 5 bytes."


def test_io_stringio_adapter() -> None:
    buf = io.StringIO("hello")
    meta = dispatch_adapter(buf)
    assert meta["metadata"]["type"] == "stringio"
    summary = deterministic_summary(meta)
    print("stringio:", summary)
    assert summary == "An in-memory text buffer of 5 characters."


@dataclass
class Point:
    x: int
    y: int


def test_dataclass_adapter() -> None:
    obj = Point(1, 2)
    meta = dispatch_adapter(obj)
    assert meta["metadata"]["type"] == "dataclass"
    summary = deterministic_summary(meta)
    print("dataclass:", summary)
    assert summary == "A structured object of type dataclass."


class Color(Enum):
    RED = 1
    BLUE = 2


def test_enum_adapter() -> None:
    meta = dispatch_adapter(Color.RED)
    assert meta["metadata"]["type"] == "enum"
    summary = deterministic_summary(meta)
    print("enum:", summary)
    assert summary == "A structured object of type enum."


def test_function_adapter() -> None:
    def sample_fn(x: int) -> int:
        return x + 1

    meta = dispatch_adapter(sample_fn)
    assert meta["metadata"]["type"] == "function"
    summary = deterministic_summary(meta)
    print("function:", summary)
    assert summary == "A callable function named sample_fn."
