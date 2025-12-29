"""Tests for collections adapter."""

from collections import Counter, OrderedDict, defaultdict, deque

from wut_is.adapters import dispatch_adapter
from wut_is.synthesizer import deterministic_summary


def test_list_of_ints_summary() -> None:
    meta = dispatch_adapter([1, 2, 3, 4, 5])
    assert meta["adapter_used"] == "CollectionsAdapter"
    assert meta["metadata"]["list_type"] == "ints"
    summary = deterministic_summary(meta)
    assert "Length: 5" in summary
    assert "Stats:" in summary


def test_list_of_dicts_schema() -> None:
    data = [{"a": 1, "b": "x"}, {"a": 2, "b": "y"}]
    meta = dispatch_adapter(data)
    assert meta["metadata"]["list_type"] == "list_of_dicts"
    assert "schema" in meta["metadata"]


def test_tuple_metadata() -> None:
    meta = dispatch_adapter((1, "x", 3.0))
    assert meta["metadata"]["type"] == "tuple"
    summary = deterministic_summary(meta)
    assert "Element types" in summary


def test_ordered_dict_metadata() -> None:
    obj = OrderedDict([("a", 1), ("b", 2)])
    meta = dispatch_adapter(obj)
    assert meta["metadata"]["type"] == "ordered_dict"
    summary = deterministic_summary(meta)
    assert "Keys:" in summary


def test_defaultdict_metadata() -> None:
    obj = defaultdict(list)
    obj["a"].append(1)
    meta = dispatch_adapter(obj)
    assert meta["metadata"]["type"] == "defaultdict"


def test_counter_metadata() -> None:
    obj = Counter({"a": 2, "b": 1})
    meta = dispatch_adapter(obj)
    assert meta["metadata"]["type"] == "counter"
    summary = deterministic_summary(meta)
    assert "Stats:" in summary


def test_deque_metadata() -> None:
    obj = deque([1, 2, 3, 4])
    meta = dispatch_adapter(obj)
    assert meta["metadata"]["type"] == "deque"


def test_range_metadata() -> None:
    obj = range(0, 10, 2)
    meta = dispatch_adapter(obj)
    assert meta["metadata"]["type"] == "range"
    summary = deterministic_summary(meta)
    assert "Length: 5" in summary
