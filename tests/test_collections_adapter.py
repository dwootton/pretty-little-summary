"""Tests for collections adapter."""

from collections import Counter, OrderedDict, defaultdict, deque

from pretty_little_summary.adapters import dispatch_adapter
from pretty_little_summary.synthesizer import deterministic_summary


def test_list_of_ints_summary() -> None:
    meta = dispatch_adapter([1, 2, 3, 4, 5])
    assert meta["adapter_used"] == "CollectionsAdapter"
    assert meta["metadata"]["list_type"] == "ints"
    summary = deterministic_summary(meta)
    print("list_ints:", summary)
    assert summary == "A list of 5 integers."


def test_list_of_dicts_schema() -> None:
    data = [{"a": 1, "b": "x"}, {"a": 2, "b": "y"}]
    meta = dispatch_adapter(data)
    assert meta["metadata"]["list_type"] == "list_of_dicts"
    assert "schema" in meta["metadata"]
    summary = deterministic_summary(meta)
    print("list_dicts:", summary)
    assert summary == "A list of 2 records with 2 consistent fields."


def test_tuple_metadata() -> None:
    meta = dispatch_adapter((1, "x", 3.0))
    assert meta["metadata"]["type"] == "tuple"
    summary = deterministic_summary(meta)
    print("tuple:", summary)
    assert summary == "A tuple of 3 elements."


def test_ordered_dict_metadata() -> None:
    obj = OrderedDict([("a", 1), ("b", 2)])
    meta = dispatch_adapter(obj)
    assert meta["metadata"]["type"] == "ordered_dict"
    summary = deterministic_summary(meta)
    print("ordered_dict:", summary)
    assert summary == "A ordered_dict with 2 keys."


def test_defaultdict_metadata() -> None:
    obj = defaultdict(list)
    obj["a"].append(1)
    meta = dispatch_adapter(obj)
    assert meta["metadata"]["type"] == "defaultdict"
    summary = deterministic_summary(meta)
    print("defaultdict:", summary)
    assert summary == "A defaultdict with 1 keys."


def test_counter_metadata() -> None:
    obj = Counter({"a": 2, "b": 1})
    meta = dispatch_adapter(obj)
    assert meta["metadata"]["type"] == "counter"
    summary = deterministic_summary(meta)
    print("counter:", summary)
    assert "Counter with 2 unique elements" in summary


def test_deque_metadata() -> None:
    obj = deque([1, 2, 3, 4])
    meta = dispatch_adapter(obj)
    assert meta["metadata"]["type"] == "deque"
    summary = deterministic_summary(meta)
    print("deque:", summary)
    assert summary == "A deque of 4 items."


def test_range_metadata() -> None:
    obj = range(0, 10, 2)
    meta = dispatch_adapter(obj)
    assert meta["metadata"]["type"] == "range"
    summary = deterministic_summary(meta)
    print("range:", summary)
    assert summary == "A range from 0 to 10 with step 2."
