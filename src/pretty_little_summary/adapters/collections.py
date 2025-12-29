"""Adapters for core collection types."""

from __future__ import annotations

from collections import Counter, OrderedDict, defaultdict, deque
import types
from typing import Any, Iterable

from pretty_little_summary.adapters._base import AdapterRegistry
from pretty_little_summary.core import MetaDescription
from pretty_little_summary.descriptor_registry import DescribeConfigRegistry
from pretty_little_summary.descriptor_utils import (
    compute_cardinality,
    compute_numeric_stats,
    safe_repr,
    safe_sample,
)


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
        stats = compute_numeric_stats([int(v) for v in samples if isinstance(v, int)])
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
        for key, val in item.items():
            key_str = str(key)
            key_counts[key_str] += 1
            key_types.setdefault(key_str, set()).add(type(val).__name__)

    consistent_keys = [
        key for key, count in key_counts.items() if count >= int(0.8 * len(samples))
    ]
    schema = {key: sorted(list(key_types[key])) for key in consistent_keys}
    sample_records = [safe_repr(item, config.max_sample_repr) for item in samples[:3]]

    return {
        "list_type": "list_of_dicts",
        "schema": schema,
        "sample_records": sample_records,
        "consistent_key_count": len(consistent_keys),
    }


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
        metadata["depth"] = _estimate_depth(values, max_depth=config.max_depth)

    return metadata


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


def _estimate_depth(obj: Any, current: int = 0, max_depth: int = 5) -> int:
    if current >= max_depth:
        return current
    if isinstance(obj, dict):
        if not obj:
            return current + 1
        return max(_estimate_depth(v, current + 1, max_depth) for v in obj.values())
    if isinstance(obj, list):
        if not obj:
            return current + 1
        return max(_estimate_depth(item, current + 1, max_depth) for item in obj[:5])
    return current


def _is_iterator(obj: Any) -> bool:
    return hasattr(obj, "__iter__") and hasattr(obj, "__next__")


AdapterRegistry.register(CollectionsAdapter)


def _build_nl_summary(metadata: dict[str, Any]) -> str:
    ctype = metadata.get("type")
    if ctype == "list":
        length = metadata.get("length")
        list_type = metadata.get("list_type")
        if list_type == "list_of_dicts":
            return (
                f"A list of {length} records with {metadata.get('consistent_key_count')} "
                "consistent fields."
            )
        if list_type == "ints":
            return f"A list of {length} integers."
        if list_type == "list_of_lists":
            return f"A 2D list with {metadata.get('rows')} rows."
        return f"A list of {length} items."
    if ctype == "tuple":
        return f"A tuple of {metadata.get('length')} elements."
    if ctype in {"set", "frozenset"}:
        return f"A {ctype} of {metadata.get('length')} unique items."
    if ctype in {"dict", "ordered_dict", "defaultdict"}:
        return f"A {ctype} with {metadata.get('length')} keys."
    if ctype == "counter":
        return (
            f"A Counter with {metadata.get('length')} unique elements totaling "
            f"{metadata.get('total_count')} observations."
        )
    if ctype == "deque":
        return f"A deque of {metadata.get('length')} items."
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
