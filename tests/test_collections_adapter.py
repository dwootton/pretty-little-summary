"""Tests for collections adapter."""

from pretty_little_summary.adapters import dispatch_adapter
from pretty_little_summary.synthesizer import deterministic_summary
from tests.input import build_input, expected_output, load_example


def test_list_of_ints_summary() -> None:
    example = load_example("list_of_ints_summary")
    meta = dispatch_adapter(build_input(example))
    assert meta["adapter_used"] == "CollectionsAdapter"
    assert meta["metadata"]["list_type"] == "ints"
    summary = deterministic_summary(meta)
    print("list_ints:", summary)
    assert summary == expected_output(example, meta)


def test_list_of_dicts_schema() -> None:
    example = load_example("list_of_dicts_schema")
    meta = dispatch_adapter(build_input(example))
    assert meta["metadata"]["list_type"] == "list_of_dicts"
    assert "schema" in meta["metadata"]
    summary = deterministic_summary(meta)
    print("list_dicts:", summary)
    assert summary == expected_output(example, meta)


def test_tuple_metadata() -> None:
    example = load_example("tuple_metadata")
    meta = dispatch_adapter(build_input(example))
    assert meta["metadata"]["type"] == "tuple"
    summary = deterministic_summary(meta)
    print("tuple:", summary)
    assert summary == expected_output(example, meta)


def test_ordered_dict_metadata() -> None:
    example = load_example("ordered_dict_metadata")
    meta = dispatch_adapter(build_input(example))
    assert meta["metadata"]["type"] == "ordered_dict"
    summary = deterministic_summary(meta)
    print("ordered_dict:", summary)
    assert summary == expected_output(example, meta)


def test_defaultdict_metadata() -> None:
    example = load_example("defaultdict_metadata")
    meta = dispatch_adapter(build_input(example))
    assert meta["metadata"]["type"] == "defaultdict"
    summary = deterministic_summary(meta)
    print("defaultdict:", summary)
    assert summary == expected_output(example, meta)


def test_counter_metadata() -> None:
    example = load_example("counter_metadata")
    meta = dispatch_adapter(build_input(example))
    assert meta["metadata"]["type"] == "counter"
    summary = deterministic_summary(meta)
    print("counter:", summary)
    assert summary == expected_output(example, meta)


def test_deque_metadata() -> None:
    example = load_example("deque_metadata")
    meta = dispatch_adapter(build_input(example))
    assert meta["metadata"]["type"] == "deque"
    summary = deterministic_summary(meta)
    print("deque:", summary)
    assert summary == expected_output(example, meta)


def test_range_metadata() -> None:
    example = load_example("range_metadata")
    meta = dispatch_adapter(build_input(example))
    assert meta["metadata"]["type"] == "range"
    summary = deterministic_summary(meta)
    print("range:", summary)
    assert summary == expected_output(example, meta)
