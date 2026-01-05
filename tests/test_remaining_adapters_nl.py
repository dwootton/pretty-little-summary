"""NL summary tests for remaining adapters."""

import asyncio

import pytest

from pretty_little_summary.adapters import dispatch_adapter
from pretty_little_summary.synthesizer import deterministic_summary
from tests.input import build_input, expected_output, load_example


def test_generic_adapter_nl() -> None:
    example = load_example("generic_adapter_nl")
    meta = dispatch_adapter(build_input(example))
    summary = deterministic_summary(meta)
    assert summary == expected_output(example, meta)


def test_async_adapter_nl() -> None:
    async def sample():
        return 1

    coro = sample()
    meta = dispatch_adapter(coro)
    summary = deterministic_summary(meta)
    expected = f"An async {meta['metadata']['type']} in state {meta['metadata']['state']}."
    assert summary == expected

    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    task = loop.create_task(sample())
    meta = dispatch_adapter(task)
    summary = deterministic_summary(meta)
    expected = f"An async {meta['metadata']['type']} in state {meta['metadata']['state']}."
    assert summary == expected

    fut = asyncio.Future()
    meta = dispatch_adapter(fut)
    summary = deterministic_summary(meta)
    expected = f"An async {meta['metadata']['type']} in state {meta['metadata']['state']}."
    assert summary == expected


def test_traceback_adapter_nl() -> None:
    example = load_example("traceback_adapter")
    meta = dispatch_adapter(build_input(example))
    summary = deterministic_summary(meta)
    assert summary == expected_output(example, meta)


networkx = pytest.importorskip("networkx")


def test_networkx_adapter_nl() -> None:
    example = load_example("networkx_adapter_nl")
    meta = dispatch_adapter(build_input(example))
    summary = deterministic_summary(meta)
    assert summary == expected_output(example, meta)


requests = pytest.importorskip("requests")


def test_requests_adapter_nl() -> None:
    example = load_example("requests_adapter_nl")
    meta = dispatch_adapter(build_input(example))
    summary = deterministic_summary(meta)
    assert summary == expected_output(example, meta)


polars = pytest.importorskip("polars")


def test_polars_adapter_nl() -> None:
    example = load_example("polars_adapter_nl")
    meta = dispatch_adapter(build_input(example))
    summary = deterministic_summary(meta)
    assert summary == expected_output(example, meta)


pydantic = pytest.importorskip("pydantic")


def test_pydantic_adapter_nl() -> None:
    example = load_example("pydantic_adapter_nl")
    meta = dispatch_adapter(build_input(example))
    summary = deterministic_summary(meta)
    assert summary == expected_output(example, meta)


torch = pytest.importorskip("torch")


def test_pytorch_adapter_nl() -> None:
    example = load_example("pytorch_adapter_nl")
    meta = dispatch_adapter(build_input(example))
    summary = deterministic_summary(meta)
    assert summary == expected_output(example, meta)


xarray = pytest.importorskip("xarray")


def test_xarray_adapter_nl() -> None:
    example = load_example("xarray_adapter_nl")
    meta = dispatch_adapter(build_input(example))
    summary = deterministic_summary(meta)
    assert summary == expected_output(example, meta)
