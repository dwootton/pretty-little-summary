"""Tests for collections adapter."""

import pytest

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


def test_deeply_nested_dict_reports_depth_and_singular_key() -> None:
    value: dict = {"leaf": True}
    for _ in range(60):
        value = {"child": value}

    meta = dispatch_adapter(value)

    assert meta["metadata"]["depth"] == 60
    assert deterministic_summary(meta) == (
        "A dict with 1 key (str -> dict), nested 60 levels deep. Keys: 'child'."
    )


# ---------------------------------------------------------------------------
# JSON-shaped dicts: a wrapper object holding one or more lists of records
# ---------------------------------------------------------------------------


def _wrapper_doc(daily_days: int = 128) -> dict:
    return {
        "dataset": "gpu-cloud-price-index-history",
        "title": "GPU Cloud Price Index - Daily History",
        "window": {"start": "2026-05-11", "end": "2026-09-15", "days": daily_days},
        "daily": [
            {
                "date": f"2026-05-{(i % 28) + 1:02d}",
                "provider_count": 9,
                "price_hourly_usd": {
                    "min": 0.059,
                    "median": 2.7 + i * 0.001,
                    "max": 60.0,
                    "count": 62 + i,
                },
            }
            for i in range(daily_days)
        ],
        "by_gpu_model": {
            "H100": [
                {"date": "2026-05-11", "price_hourly_usd": {"min": 3.4, "median": 14.0}}
            ]
        },
    }


def test_wrapper_dict_describes_record_tables_by_path() -> None:
    meta = dispatch_adapter(_wrapper_doc())
    metadata = meta["metadata"]

    assert metadata["record_table_count"] == 2
    assert set(metadata["record_tables"]) == {"daily", "by_gpu_model.H100"}
    assert metadata["record_tables"]["daily"]["record_count"] == 128
    assert metadata["record_tables"]["by_gpu_model.H100"]["record_count"] == 1

    summary = deterministic_summary(meta)
    assert "holding 2 record tables" in summary
    assert "daily (128 records, 6 fields)" in summary
    assert "by_gpu_model.H100 (1 record, 3 fields)" in summary


def test_wrapper_dict_flattens_nested_fields_with_stats() -> None:
    meta = dispatch_adapter(_wrapper_doc())
    daily = meta["metadata"]["record_tables"]["daily"]

    assert daily["schema"]["price_hourly_usd.median"] == ["float"]
    assert daily["schema"]["date"] == ["str"]
    assert "price_hourly_usd" not in daily["schema"]

    stats = daily["field_stats"]
    assert "range" in stats["price_hourly_usd.median"]
    assert "mean" in stats["price_hourly_usd.median"]
    # Non-numeric fields get no stats.
    assert "date" not in stats


def test_list_of_dicts_flattens_when_reached_directly() -> None:
    meta = dispatch_adapter(_wrapper_doc()["daily"])
    metadata = meta["metadata"]

    assert metadata["list_type"] == "list_of_dicts"
    assert sorted(metadata["schema"]) == [
        "date",
        "price_hourly_usd.count",
        "price_hourly_usd.max",
        "price_hourly_usd.median",
        "price_hourly_usd.min",
        "provider_count",
    ]
    assert deterministic_summary(meta) == "A list of 128 records with 6 consistent fields."


def test_dict_without_record_lists_is_unchanged() -> None:
    value = {"a": 1, "b": {"c": 2}, "d": "text"}
    meta = dispatch_adapter(value)

    summary = deterministic_summary(meta)
    assert "record_tables" not in meta["metadata"]
    assert summary.startswith("A dict with 3 keys (str -> ")
    assert summary.endswith("Keys: 'a', 'b', 'd'.")
    assert "record table" not in summary


def test_dict_of_scalar_lists_is_not_a_record_table() -> None:
    value = {"temps": [1, 2, 3], "labels": ["a", "b"]}
    meta = dispatch_adapter(value)

    assert "record_tables" not in meta["metadata"]
    assert "record table" not in deterministic_summary(meta)


def test_record_tables_beyond_the_cap_are_reported_as_truncated() -> None:
    value = {f"table_{i}": [{"x": i, "y": i * 2}] for i in range(7)}
    meta = dispatch_adapter(value)
    metadata = meta["metadata"]

    assert metadata["record_table_count"] == 4
    assert metadata["record_tables_truncated"] == 3
    assert "3 more not described" in deterministic_summary(meta)


def test_schema_flattening_is_capped_and_reports_truncation() -> None:
    record = {f"f{i}": {"inner": i} for i in range(50)}
    meta = dispatch_adapter([record, record])
    metadata = meta["metadata"]

    assert metadata["consistent_key_count"] == 40
    assert metadata["schema_truncated"] is True
    assert "schema shows the first 40" in deterministic_summary(meta)


# --- regressions: shapes that already worked must keep working ---------------


def test_top_level_list_of_flat_records_is_unchanged() -> None:
    values = [{"name": "alice", "age": 30}, {"name": "bob", "age": 25}]
    meta = dispatch_adapter(values)

    assert meta["metadata"]["schema"] == {"name": ["str"], "age": ["int"]}
    assert deterministic_summary(meta) == "A list of 2 records with 2 consistent fields."


def test_node_link_graph_dict_names_its_two_tables() -> None:
    graph = {
        "directed": False,
        "multigraph": False,
        "graph": {},
        "nodes": [{"id": "a"}, {"id": "b"}, {"id": "c"}],
        "links": [
            {"source": "a", "target": "b", "weight": 1.0},
            {"source": "b", "target": "c", "weight": 2.0},
        ],
    }
    meta = dispatch_adapter(graph)

    assert list(meta["metadata"]["record_tables"]) == ["nodes", "links"]
    summary = deterministic_summary(meta)
    assert "nodes (3 records, 1 field)" in summary
    assert "links (2 records, 3 fields)" in summary


def test_dataframe_is_still_handled_by_the_pandas_adapter() -> None:
    pd = pytest.importorskip("pandas")
    meta = dispatch_adapter(pd.DataFrame({"a": [1, 2, 3], "b": ["x", "y", "z"]}))

    assert meta["adapter_used"] == "PandasAdapter"
    assert "record table" not in deterministic_summary(meta)
