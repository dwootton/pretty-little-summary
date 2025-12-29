"""Tests for attrs adapter."""

import pytest

from pretty_little_summary.adapters import dispatch_adapter
from pretty_little_summary.synthesizer import deterministic_summary


attr = pytest.importorskip("attr")


@attr.define
class Person:
    name: str
    age: int


def test_attrs_adapter() -> None:
    obj = Person("alice", 30)
    meta = dispatch_adapter(obj)
    assert meta["adapter_used"] == "AttrsAdapter"
    assert meta["metadata"]["type"] == "attrs"
    summary = deterministic_summary(meta)
    print("attrs:", summary)
    assert summary == "An attrs class Person with 2 attributes."
