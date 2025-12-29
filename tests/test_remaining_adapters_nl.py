"""NL summary tests for remaining adapters."""

import asyncio
import types

import pytest

from pretty_little_summary.adapters import dispatch_adapter
from pretty_little_summary.synthesizer import deterministic_summary


def test_generic_adapter_nl() -> None:
    class Custom:
        pass

    meta = dispatch_adapter(Custom())
    summary = deterministic_summary(meta)
    assert summary == f"An object of type {meta['object_type']}."


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
    try:
        raise ValueError("boom")
    except ValueError as exc:
        meta = dispatch_adapter(exc.__traceback__)
    summary = deterministic_summary(meta)
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


networkx = pytest.importorskip("networkx")


def test_networkx_adapter_nl() -> None:
    import networkx as nx

    g = nx.Graph()
    g.add_edge("a", "b")
    meta = dispatch_adapter(g)
    summary = deterministic_summary(meta)
    assert summary == (
        f"A networkx graph with {meta['node_count']} nodes and {meta['edge_count']} edges."
    )


requests = pytest.importorskip("requests")


def test_requests_adapter_nl() -> None:
    import requests as rq

    resp = rq.Response()
    resp.status_code = 200
    resp.url = "https://example.com"
    meta = dispatch_adapter(resp)
    summary = deterministic_summary(meta)
    assert summary == f"An HTTP response with status {meta['status_code']}."


polars = pytest.importorskip("polars")


def test_polars_adapter_nl() -> None:
    import polars as pl

    df = pl.DataFrame({"a": [1, 2], "b": ["x", "y"]})
    meta = dispatch_adapter(df)
    summary = deterministic_summary(meta)
    parts = [f"A Polars DataFrame with shape {meta.get('shape')}."]
    schema = meta.get("schema") or {}
    if schema:
        cols = []
        for name, dtype in list(schema.items())[:3]:
            cols.append(f"{name} ({dtype})")
        if cols:
            parts.append(f"Schema: {', '.join(cols)}.")
    sample_rows = meta.get("metadata", {}).get("sample_rows")
    if sample_rows:
        parts.append(f"Sample row: {sample_rows[0]}.")
    elif meta.get("metadata", {}).get("sample_rows_omitted"):
        parts.append("Sample rows omitted for size/perf.")
    assert summary == " ".join(parts)


pydantic = pytest.importorskip("pydantic")


def test_pydantic_adapter_nl() -> None:
    from pydantic import BaseModel

    class User(BaseModel):
        name: str
        age: int

    user = User(name="alice", age=30)
    meta = dispatch_adapter(user)
    summary = deterministic_summary(meta)
    assert summary == f"A Pydantic model {meta['object_type']}."


torch = pytest.importorskip("torch")


def test_pytorch_adapter_nl() -> None:
    import torch as t

    tensor = t.tensor([1.0, 2.0])
    meta = dispatch_adapter(tensor)
    summary = deterministic_summary(meta)
    assert summary == f"A PyTorch tensor with shape {meta['metadata']['shape']}."


xarray = pytest.importorskip("xarray")


def test_xarray_adapter_nl() -> None:
    import xarray as xr

    arr = xr.DataArray([[1, 2], [3, 4]], dims=["x", "y"])
    meta = dispatch_adapter(arr)
    summary = deterministic_summary(meta)
    assert summary == (
        f"An xarray object {meta['object_type']} with shape {meta.get('shape')}. "
        "Sample: [1, 2, 3, 4]."
    )
