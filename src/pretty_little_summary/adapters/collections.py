"""Adapters for core collection types."""

from __future__ import annotations

import types
from collections import Counter, OrderedDict, defaultdict, deque
from collections.abc import Iterable
from typing import Any

from pretty_little_summary.adapters._base import AdapterRegistry, module_loaded
from pretty_little_summary.core import MetaDescription
from pretty_little_summary.descriptor_registry import DescribeConfigRegistry
from pretty_little_summary.descriptor_utils import (
    compute_numeric_stats,
    format_count,
    oxford_comma,
    safe_repr,
    safe_sample,
)

# Bounds for descending into JSON-shaped dicts. The common shape of a JSON file
# is a wrapper object holding one or more lists of records ("daily": [...]) or a
# dict of such lists keyed by series name ("by_gpu_model": {"H100": [...]}), so
# the descent goes two levels and no further. Every limit below exists so that a
# pathological document costs a bounded amount of work, never a full scan.
MAX_NESTED_TABLES = 4  # record tables described per dict
MAX_NESTED_LEVELS = 2  # dict nesting levels searched for those tables
MAX_KEYS_SCANNED = 500  # keys examined per dict while searching
RECORD_PROBE = 5  # leading items checked to call a list a record table
MAX_TABLE_SAMPLE = 200  # records read per table when computing field stats
MAX_FLAT_DEPTH = 3  # nesting levels folded into dotted field paths
MAX_FLAT_FIELDS = 40  # dotted fields reported in one schema
MAX_RECORD_FIELDS = 200  # dotted fields read out of one record before stopping


class CollectionsAdapter:
    """Adapter for built-in collection types and iterators."""

    @staticmethod
    def can_handle(obj: Any) -> bool:
        if isinstance(obj, (list, tuple, dict, set, frozenset, range)):
            return True
        if isinstance(obj, (OrderedDict, defaultdict, Counter, deque)):
            return True
        if isinstance(obj, types.GeneratorType):
            return True
        if _is_iterator(obj):
            return True
        return False

    @staticmethod
    def extract_metadata(obj: Any) -> MetaDescription:
        config = DescribeConfigRegistry.get()
        meta: MetaDescription = {
            "object_type": f"{type(obj).__module__}.{type(obj).__name__}",
            "adapter_used": "CollectionsAdapter",
        }

        metadata: dict[str, Any] = {}

        if isinstance(obj, list):
            metadata.update(_describe_list(obj, config))
        elif isinstance(obj, tuple) and not _is_namedtuple(obj):
            metadata.update(_describe_tuple(obj, config))
        elif isinstance(obj, OrderedDict):
            metadata.update(_describe_ordered_dict(obj, config))
        elif isinstance(obj, defaultdict):
            metadata.update(_describe_defaultdict(obj, config))
        elif isinstance(obj, Counter):
            metadata.update(_describe_counter(obj, config))
        elif isinstance(obj, deque):
            metadata.update(_describe_deque(obj, config))
        elif isinstance(obj, dict):
            metadata.update(_describe_dict(obj, config))
        elif isinstance(obj, set):
            metadata.update(_describe_set(obj, config, is_frozen=False))
        elif isinstance(obj, frozenset):
            metadata.update(_describe_set(obj, config, is_frozen=True))
        elif isinstance(obj, range):
            metadata.update(_describe_range(obj))
        elif isinstance(obj, types.GeneratorType):
            metadata.update(_describe_generator(obj, config))
        elif _is_iterator(obj):
            metadata.update(_describe_iterator(obj, config))
        else:
            metadata["value"] = safe_repr(obj, config.max_sample_repr)

        if metadata:
            meta["metadata"] = metadata
            meta["nl_summary"] = _build_nl_summary(metadata)

        return meta


def _describe_list(values: list[Any], config) -> dict[str, Any]:
    metadata: dict[str, Any] = {"type": "list", "length": len(values)}
    samples, _, _ = safe_sample(values, n=config.sample_size)
    metadata["sample_items"] = [safe_repr(v, config.max_sample_repr) for v in samples]

    if values:
        element_types = list({type(v).__name__ for v in samples})
        metadata["element_types"] = element_types

    if values and all(isinstance(v, int) and not isinstance(v, bool) for v in samples):
        stats_pool = values[:10000] if len(values) > config.sample_size else samples
        stats = compute_numeric_stats([int(v) for v in stats_pool if isinstance(v, int)])
        if stats:
            metadata["stats"] = stats.to_prose()
        metadata["list_type"] = "ints"
    elif values and all(isinstance(v, dict) for v in samples):
        metadata.update(_describe_list_of_dicts(values, config))
    elif values and all(isinstance(v, list) for v in samples):
        metadata.update(_describe_list_of_lists(values, config))
    elif values:
        type_counts = Counter(type(v).__name__ for v in samples)
        if len(type_counts) > 1:
            metadata["list_type"] = "heterogeneous"
            metadata["type_distribution"] = dict(type_counts)

    return metadata


def _describe_list_of_dicts(values: list[dict], config) -> dict[str, Any]:
    samples, _, _ = safe_sample(values, n=max(config.sample_size, 3))
    key_counts: Counter[str] = Counter()
    key_types: dict[str, set[str]] = {}
    for item in samples:
        if not isinstance(item, dict):
            continue
        # Nested dict fields are folded into dotted paths, so a field reads
        # "price_hourly_usd.median": ["float"] rather than the useless
        # "price_hourly_usd": ["dict"].
        for key, val in _flatten_record(item, MAX_FLAT_DEPTH).items():
            key_counts[key] += 1
            key_types.setdefault(key, set()).add(type(val).__name__)

    consistent_keys = [
        key for key, count in key_counts.items() if count >= int(0.8 * len(samples))
    ]
    shown_keys = consistent_keys[:MAX_FLAT_FIELDS]
    schema = {key: sorted(key_types[key]) for key in shown_keys}
    sample_records = [safe_repr(item, config.max_sample_repr) for item in samples[:3]]

    metadata: dict[str, Any] = {
        "list_type": "list_of_dicts",
        "schema": schema,
        "sample_records": sample_records,
        "consistent_key_count": len(shown_keys),
    }
    if len(consistent_keys) > len(shown_keys):
        metadata["consistent_key_total"] = len(consistent_keys)
        metadata["schema_truncated"] = True

    field_stats, stats_sample = _numeric_field_stats(values, shown_keys)
    if field_stats:
        metadata["field_stats"] = field_stats
    if stats_sample is not None:
        metadata["stats_sample_size"] = stats_sample

    profile = _pandas_record_profile(values, shown_keys)
    if profile:
        metadata["pandas_profile"] = profile

    return metadata


def _flatten_record(record: dict[Any, Any], max_depth: int, prefix: str = "") -> dict[str, Any]:
    """Fold nested dict fields into dotted paths, stopping at ``max_depth``."""
    flat: dict[str, Any] = {}
    for key, val in record.items():
        path = f"{prefix}{key}"
        if isinstance(val, dict) and val and max_depth > 1:
            flat.update(_flatten_record(val, max_depth - 1, f"{path}."))
        else:
            flat[path] = val
        if len(flat) >= MAX_RECORD_FIELDS:
            break
    return flat


def _numeric_field_stats(
    values: list[dict], fields: list[str]
) -> tuple[dict[str, str], int | None]:
    """Range/mean prose for each field that is numeric across a bounded sample."""
    if not fields:
        return {}, None
    pool = values[:MAX_TABLE_SAMPLE]
    columns: dict[str, list[float]] = {field: [] for field in fields}
    numeric: dict[str, bool] = {field: True for field in fields}
    for record in pool:
        if not isinstance(record, dict):
            continue
        flat = _flatten_record(record, MAX_FLAT_DEPTH)
        for field in fields:
            if not numeric[field] or field not in flat:
                continue
            val = flat[field]
            if isinstance(val, bool) or not isinstance(val, (int, float)):
                numeric[field] = False
                continue
            columns[field].append(float(val))

    stats: dict[str, str] = {}
    for field in fields:
        if not numeric[field] or not columns[field]:
            continue
        computed = compute_numeric_stats(columns[field])
        if computed:
            stats[field] = computed.to_prose()
    sampled = len(pool) if len(values) > len(pool) else None
    return stats, sampled


def _pandas_record_profile(values: list[dict], fields: list[str]) -> dict[str, Any] | None:
    """Optional pandas enrichment: dtypes, nulls and cardinality per field.

    Only runs when pandas is *already imported* by the caller's program — pls
    never pulls it in itself, and the stdlib schema above stands on its own.
    Purely additive metadata: the nl_summary never depends on it.
    """
    if not fields or not module_loaded("pandas"):
        return None
    try:
        import pandas as pd

        frame = pd.json_normalize(values[:MAX_TABLE_SAMPLE], max_level=MAX_FLAT_DEPTH - 1)
        present = [field for field in fields if field in frame.columns]
        if not present:
            return None
        frame = frame[present]
        profile: dict[str, Any] = {
            "dtypes": {field: str(frame[field].dtype) for field in present},
            "rows_profiled": len(frame),
        }
        nulls = {
            field: int(count) for field, count in frame.isna().sum().items() if int(count) > 0
        }
        if nulls:
            profile["null_counts"] = nulls
        profile["unique_counts"] = {field: int(frame[field].nunique()) for field in present}
        return profile
    except Exception:
        return None


def _describe_list_of_lists(values: list[list[Any]], config) -> dict[str, Any]:
    samples, _, _ = safe_sample(values, n=max(config.sample_size, 3))
    lengths = [len(row) for row in samples if isinstance(row, list)]
    is_rectangular = len(set(lengths)) == 1 if lengths else False
    metadata: dict[str, Any] = {
        "list_type": "list_of_lists",
        "rows": len(values),
        "row_lengths": lengths[: config.sample_size],
        "rectangular": is_rectangular,
    }
    if is_rectangular and lengths:
        metadata["shape"] = (len(values), lengths[0])

    flattened: list[Any] = []
    for row in samples:
        if isinstance(row, list):
            flattened.extend(row[: config.sample_size])
    if flattened:
        element_types = list({type(v).__name__ for v in flattened})
        metadata["element_types"] = element_types
        if all(isinstance(v, (int, float)) for v in flattened):
            stats = compute_numeric_stats([v for v in flattened if isinstance(v, (int, float))])
            if stats:
                metadata["stats"] = stats.to_prose()
    return metadata


def _describe_tuple(values: tuple[Any, ...], config) -> dict[str, Any]:
    metadata: dict[str, Any] = {
        "type": "tuple",
        "length": len(values),
    }
    samples = values[: config.sample_size]
    metadata["sample_items"] = [safe_repr(v, config.max_sample_repr) for v in samples]
    metadata["element_types"] = [type(v).__name__ for v in samples]
    return metadata


def _describe_dict(values: dict[Any, Any], config) -> dict[str, Any]:
    metadata: dict[str, Any] = {"type": "dict", "length": len(values)}
    items = list(values.items())[: config.sample_size]
    metadata["keys"] = [safe_repr(k, config.max_sample_repr) for k, _ in items]
    metadata["sample_items"] = {safe_repr(k, 30): type(v).__name__ for k, v in items}

    key_types = list({type(k).__name__ for k in values.keys()})
    value_types = list({type(v).__name__ for v in values.values()})
    metadata["key_types"] = key_types[: config.sample_size]
    metadata["value_types"] = value_types[: config.sample_size]

    if values and all(isinstance(k, str) for k in list(values.keys())[:10]) and all(
        isinstance(v, int) and not isinstance(v, bool) for v in list(values.values())[:10]
    ):
        stats = compute_numeric_stats([v for v in list(values.values())[:10000]])
        if stats:
            metadata["stats"] = stats.to_prose()
        metadata["mapping_type"] = "str_to_int"

    if _has_nested(values):
        metadata["nested"] = True
        depth, depth_truncated = _estimate_depth(values)
        metadata["depth"] = depth
        if depth_truncated:
            metadata["depth_truncated"] = True
        metadata.update(_describe_nested_tables(values, config))

    return metadata


def _is_record_list(value: Any) -> bool:
    """True for a list whose leading items are all dicts — i.e. a record table."""
    if not isinstance(value, list) or not value:
        return False
    probe = value[:RECORD_PROBE]
    return all(isinstance(item, dict) for item in probe)


def _find_record_tables(values: dict[Any, Any]) -> tuple[list[tuple[str, list]], int]:
    """Find record tables under a dict, keyed by dotted path.

    Searches the dict's own values and, one level further, the values of any
    dict it holds — the "list under a key" and "dict of lists keyed by series
    name" shapes. Returns the tables found (capped) and how many more were seen
    but not described.
    """
    found: list[tuple[str, list]] = []
    extra = 0
    queue: list[tuple[str, dict[Any, Any], int]] = [("", values, 1)]

    while queue:
        prefix, mapping, level = queue.pop(0)
        for index, (key, val) in enumerate(mapping.items()):
            if index >= MAX_KEYS_SCANNED:
                break
            path = f"{prefix}.{key}" if prefix else str(key)
            if _is_record_list(val):
                if len(found) >= MAX_NESTED_TABLES:
                    extra += 1
                else:
                    found.append((path, val))
            elif isinstance(val, dict) and val and level < MAX_NESTED_LEVELS:
                queue.append((path, val, level + 1))

    return found, extra


def _describe_nested_tables(values: dict[Any, Any], config) -> dict[str, Any]:
    tables, extra = _find_record_tables(values)
    if not tables:
        return {}
    described: dict[str, Any] = {}
    for path, table in tables:
        entry = _describe_list_of_dicts(table, config)
        entry["record_count"] = len(table)
        described[path] = entry
    metadata: dict[str, Any] = {
        "record_tables": described,
        "record_table_count": len(described),
    }
    if extra:
        metadata["record_tables_truncated"] = extra
    return metadata


def _format_record_tables(metadata: dict[str, Any]) -> str:
    tables: dict[str, Any] = metadata.get("record_tables") or {}
    if not tables:
        return ""
    parts = [
        f"{path} ({format_count(entry['record_count'], 'record')}, "
        f"{format_count(entry['consistent_key_count'], 'field')})"
        for path, entry in tables.items()
    ]
    extra = metadata.get("record_tables_truncated")
    if extra:
        parts.append(f"{extra} more not described")
    noun = format_count(len(tables), "record table")
    return f", holding {noun}: {oxford_comma(parts)}"


def _describe_ordered_dict(values: OrderedDict, config) -> dict[str, Any]:
    metadata = _describe_dict(values, config)
    metadata["type"] = "ordered_dict"
    metadata["ordered"] = True
    return metadata


def _describe_defaultdict(values: defaultdict, config) -> dict[str, Any]:
    metadata = _describe_dict(values, config)
    metadata["type"] = "defaultdict"
    default_factory = values.default_factory
    if default_factory:
        metadata["default_factory"] = getattr(default_factory, "__name__", str(default_factory))
    return metadata


def _describe_counter(values: Counter, config) -> dict[str, Any]:
    metadata: dict[str, Any] = {"type": "counter", "length": len(values)}
    most_common = values.most_common(5)
    metadata["most_common"] = most_common
    total = sum(values.values())
    metadata["total_count"] = total
    if values:
        counts = list(values.values())[:10000]
        stats = compute_numeric_stats(counts)
        if stats:
            metadata["stats"] = stats.to_prose()
    return metadata


def _describe_deque(values: deque, config) -> dict[str, Any]:
    metadata: dict[str, Any] = {"type": "deque", "length": len(values)}
    metadata["maxlen"] = values.maxlen
    if values:
        front = list(values)[:3]
        back = list(values)[-3:]
        metadata["front_sample"] = [safe_repr(v, config.max_sample_repr) for v in front]
        metadata["back_sample"] = [safe_repr(v, config.max_sample_repr) for v in back]
    return metadata


def _describe_set(values: Iterable[Any], config, is_frozen: bool) -> dict[str, Any]:
    items = list(values)
    metadata: dict[str, Any] = {
        "type": "frozenset" if is_frozen else "set",
        "length": len(items),
    }
    samples = items[: config.sample_size]
    metadata["sample_items"] = [safe_repr(v, config.max_sample_repr) for v in samples]
    metadata["element_types"] = list({type(v).__name__ for v in samples})
    if samples and all(isinstance(v, (int, float)) for v in samples):
        stats = compute_numeric_stats([v for v in samples if isinstance(v, (int, float))])
        if stats:
            metadata["stats"] = stats.to_prose()
    return metadata


def _describe_range(value: range) -> dict[str, Any]:
    length = len(value)
    metadata: dict[str, Any] = {
        "type": "range",
        "start": value.start,
        "stop": value.stop,
        "step": value.step,
        "length": length,
    }
    if length:
        sample = [value[0], value[1], value[2]] if length >= 3 else list(value)
        tail = [value[-3], value[-2], value[-1]] if length >= 3 else []
        metadata["sample_start"] = sample
        if tail:
            metadata["sample_end"] = tail
    return metadata


def _describe_iterator(value: Any, config) -> dict[str, Any]:
    metadata: dict[str, Any] = {"type": "iterator", "name": type(value).__name__}
    if config.allow_iterator_consumption:
        samples = list(_consume_iterator(value, config.sample_size + 1))
        metadata["sample_items"] = [safe_repr(v, config.max_sample_repr) for v in samples]
        metadata["consumed"] = True
    else:
        metadata["consumed"] = False
    return metadata


def _describe_generator(value: types.GeneratorType, config) -> dict[str, Any]:
    metadata: dict[str, Any] = {
        "type": "generator",
        "name": value.gi_code.co_name,
        "qualname": value.gi_code.co_qualname,
        "exhausted": value.gi_frame is None,
    }
    if config.allow_iterator_consumption and value.gi_frame is not None:
        samples = list(_consume_iterator(value, config.sample_size + 1))
        metadata["sample_items"] = [safe_repr(v, config.max_sample_repr) for v in samples]
        metadata["consumed"] = True
    else:
        metadata["consumed"] = False
    return metadata


def _consume_iterator(value: Any, n: int) -> list[Any]:
    result = []
    for _ in range(n):
        try:
            result.append(next(value))
        except StopIteration:
            break
    return result


def _is_namedtuple(obj: Any) -> bool:
    return isinstance(obj, tuple) and hasattr(obj, "_fields")


def _has_nested(values: dict[Any, Any]) -> bool:
    return any(isinstance(v, (dict, list)) for v in values.values())


def _estimate_depth(obj: Any, max_depth: int = 100) -> tuple[int, bool]:
    """Return nested container edges and whether the bounded scan stopped early."""
    deepest = 0
    truncated = False
    stack: list[tuple[Any, int, frozenset[int]]] = [(obj, 0, frozenset())]

    while stack:
        current, depth, ancestors = stack.pop()
        deepest = max(deepest, depth)
        if not isinstance(current, (dict, list)):
            continue

        identity = id(current)
        if identity in ancestors:
            truncated = True
            continue

        children = current.values() if isinstance(current, dict) else current[:5]
        nested_children = [child for child in children if isinstance(child, (dict, list))]
        if depth >= max_depth:
            truncated = truncated or bool(nested_children)
            continue

        next_ancestors = ancestors | {identity}
        stack.extend((child, depth + 1, next_ancestors) for child in nested_children)

    return deepest, truncated


def _is_iterator(obj: Any) -> bool:
    return hasattr(obj, "__iter__") and hasattr(obj, "__next__")


AdapterRegistry.register(CollectionsAdapter)


def _build_nl_summary(metadata: dict[str, Any]) -> str:
    ctype = metadata.get("type")
    if ctype == "list":
        length = metadata.get("length")
        list_type = metadata.get("list_type")
        if list_type == "list_of_dicts":
            shown = metadata.get("consistent_key_count")
            total = metadata.get("consistent_key_total")
            if total:
                return (
                    f"A list of {length} records with {total} consistent fields "
                    f"(schema shows the first {shown})."
                )
            return f"A list of {length} records with {shown} consistent fields."
        if list_type == "ints":
            stats = metadata.get("stats")
            stats_str = f" Stats: {stats}." if stats else ""
            return f"A list of {length} integers.{stats_str}"
        if list_type == "list_of_lists":
            return f"A 2D list with {metadata.get('rows')} rows."
        return f"A list of {length} items."
    if ctype == "tuple":
        length = metadata.get("length")
        element_types = metadata.get("element_types") or []
        sample_items = metadata.get("sample_items") or []
        types_str = ", ".join(element_types)
        sample_str = ", ".join(sample_items)
        return f"A tuple of {length} elements ({types_str}): ({sample_str})."
    if ctype in {"set", "frozenset"}:
        return f"A {ctype} of {metadata.get('length')} unique items."
    if ctype in {"ordered_dict", "defaultdict", "dict"}:
        length = metadata.get("length")
        key_word = "key" if length == 1 else "keys"
        key_types = ", ".join(metadata.get("key_types") or [])
        value_types = ", ".join(metadata.get("value_types") or [])
        types_str = f" ({key_types} -> {value_types})" if key_types and value_types else ""
        depth = metadata.get("depth")
        if depth and depth > 1:
            qualifier = "at least " if metadata.get("depth_truncated") else ""
            types_str += f", nested {qualifier}{depth} levels deep"
        stats = metadata.get("stats")
        stats_str = f" Stats: {stats}." if stats else ""
        tables_str = _format_record_tables(metadata)
        types_str += tables_str
        keys = metadata.get("keys") or []
        # With the tables named, a full key listing is redundant noise.
        keys_str = (
            ""
            if tables_str
            else (f" Keys: {', '.join(keys)}." if keys and length == len(keys) else "")
        )
        if ctype == "ordered_dict":
            return f"An OrderedDict with {length} {key_word}{types_str}.{keys_str}{stats_str}"
        if ctype == "defaultdict":
            default_factory = metadata.get("default_factory")
            factory_str = f"(default_factory={default_factory}) " if default_factory else ""
            return (
                f"A defaultdict{factory_str}with {length} {key_word}{types_str}."
                f"{keys_str}{stats_str}"
            )
        return f"A dict with {length} {key_word}{types_str}.{keys_str}{stats_str}"
    if ctype == "counter":
        most_common = metadata.get("most_common") or []
        breakdown = ", ".join(f"{item!r}: {count}" for item, count in most_common[:3])
        return (
            f"A Counter with {metadata.get('length')} unique elements totaling "
            f"{metadata.get('total_count')} observations. Most common: {breakdown}."
        )
    if ctype == "deque":
        front = metadata.get("front_sample") or []
        back = metadata.get("back_sample") or []
        front_str = ", ".join(front)
        back_str = ", ".join(back)
        return (
            f"A deque of {metadata.get('length')} items, front: [{front_str}], "
            f"back: [{back_str}]."
        )
    if ctype == "range":
        return (
            f"A range from {metadata.get('start')} to {metadata.get('stop')} "
            f"with step {metadata.get('step')}."
        )
    if ctype == "iterator":
        return f"An iterator ({metadata.get('name')})."
    if ctype == "generator":
        status = "exhausted" if metadata.get("exhausted") else "active"
        return f"A generator '{metadata.get('name')}' ({status})."
    return f"A collection of type {ctype}."
