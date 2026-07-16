"""Contract tests every adapter must satisfy.

These are invariants rather than golden values: for each example input (reusing
the tests/input gallery) and for the registry itself, assert the guarantees
`pls` promises regardless of type. This is the safety net that makes it cheap to
add or refactor adapters — including LLM-generated ones — because a new adapter
either upholds the contract or a test turns red.
"""

from __future__ import annotations

import importlib.util
import json

import pytest

import pretty_little_summary as pls
from pretty_little_summary.adapters import AdapterRegistry, dispatch_adapter, load_all_adapters
from tests.input import build_input, list_example_ids, load_example

# An adapter's textual summary must stay bounded no matter how big the input is.
MAX_CONTENT_CHARS = 50_000


def _missing_dependency(example) -> str | None:
    for module in getattr(example, "REQUIRES", []):
        if importlib.util.find_spec(module) is None:
            return module
    return None


def _describable_example_params():
    """Example ids whose dependencies are installed and don't need tmp_path."""
    params: list[object] = []
    for example_id in list_example_ids():
        example = load_example(example_id)
        if getattr(example, "REQUIRES_TMP_PATH", False):
            continue
        missing = _missing_dependency(example)
        if missing:
            params.append(
                pytest.param(example_id, marks=pytest.mark.skip(reason=f"Missing: {missing}"))
            )
            continue
        params.append(pytest.param(example_id, id=example_id))
    return params


def _build(example):
    """Build an example object, returning (obj, cleanup_or_None)."""
    obj = build_input(example)
    if isinstance(obj, tuple) and len(obj) == 2:
        return obj
    return obj, None


def _cleanup(handle) -> None:
    if handle is None:
        return
    if hasattr(handle, "close"):
        handle.close()
    elif callable(handle):
        handle()


EXAMPLE_PARAMS = _describable_example_params()


@pytest.mark.parametrize("example_id", EXAMPLE_PARAMS)
def test_describe_never_raises_and_is_wellformed(example_id: str) -> None:
    example = load_example(example_id)
    obj, cleanup = _build(example)
    try:
        result = pls.describe(obj)
    finally:
        _cleanup(cleanup)

    # content: non-empty, bounded string.
    assert isinstance(result.content, str)
    assert result.content.strip(), "content must not be empty"
    assert len(result.content) <= MAX_CONTENT_CHARS, "content must stay bounded"

    # meta: has required identity fields.
    assert isinstance(result.meta, dict)
    assert result.meta.get("object_type"), "meta must record object_type"
    assert result.meta.get("adapter_used"), "meta must record adapter_used"


@pytest.mark.parametrize("example_id", EXAMPLE_PARAMS)
def test_meta_is_json_serializable(example_id: str) -> None:
    example = load_example(example_id)
    obj, cleanup = _build(example)
    try:
        result = pls.describe(obj)
    finally:
        _cleanup(cleanup)

    # The whole point of `meta` is that it is a portable, serializable fact
    # document. Tuples are acceptable (JSON encodes them as arrays); arbitrary
    # objects, sets, and bytes are not.
    json.dumps(result.meta)


@pytest.mark.parametrize("example_id", EXAMPLE_PARAMS)
def test_describe_is_deterministic(example_id: str) -> None:
    example = load_example(example_id)

    obj1, cleanup1 = _build(example)
    try:
        first = pls.describe(obj1)
    finally:
        _cleanup(cleanup1)

    # Rebuild a fresh object: some inputs (files, iterators) are consumed by the
    # first pass, so re-describing the same instance is not a fair determinism
    # test — re-describing an equivalent instance is.
    obj2, cleanup2 = _build(example)
    try:
        second = pls.describe(obj2)
    finally:
        _cleanup(cleanup2)

    assert first.content == second.content, "content must be deterministic"
    assert json.dumps(first.meta, sort_keys=True, default=str) == json.dumps(
        second.meta, sort_keys=True, default=str
    ), "meta must be deterministic"


@pytest.mark.parametrize("example_id", EXAMPLE_PARAMS)
def test_no_unexpected_emergency_fallback(example_id: str) -> None:
    """Known-good example inputs should be handled by a real adapter path."""
    example = load_example(example_id)
    obj, cleanup = _build(example)
    try:
        result = pls.describe(obj)
    finally:
        _cleanup(cleanup)

    assert "emergency fallback" not in result.meta.get("adapter_used", "")


def test_every_registered_adapter_has_a_safe_can_handle() -> None:
    """A registered adapter must expose the protocol and never let can_handle
    raise on an arbitrary object (dispatch relies on this)."""
    load_all_adapters()

    class _Sentinel:
        pass

    sentinel = _Sentinel()
    for adapter in AdapterRegistry.adapters():
        assert callable(getattr(adapter, "can_handle", None)), f"{adapter} lacks can_handle"
        assert callable(getattr(adapter, "extract_metadata", None)), (
            f"{adapter} lacks extract_metadata"
        )
        result = adapter.can_handle(sentinel)
        assert isinstance(result, bool), f"{adapter}.can_handle must return bool"


def test_generic_adapter_is_last_in_priority() -> None:
    load_all_adapters()
    adapters = AdapterRegistry.adapters()
    assert adapters[-1].__name__ == "GenericAdapter"


def test_unknown_object_falls_back_to_generic() -> None:
    class TotallyUnknown:
        pass

    meta = dispatch_adapter(TotallyUnknown())
    assert "GenericAdapter" in meta["adapter_used"]
    assert meta["object_type"].endswith("TotallyUnknown")
