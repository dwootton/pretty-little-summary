"""NL summary tests for remaining adapters."""

import asyncio
import types

import pytest

from wut_is.adapters import dispatch_adapter
from wut_is.synthesizer import deterministic_summary


def test_generic_adapter_nl() -> None:
    class Custom:
        pass

    meta = dispatch_adapter(Custom())
    summary = deterministic_summary(meta)
    assert "An object of type" in summary


def test_async_adapter_nl() -> None:
    async def sample():
        return 1

    coro = sample()
    meta = dispatch_adapter(coro)
    summary = deterministic_summary(meta)
    assert "async" in summary

    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    task = loop.create_task(sample())
    meta = dispatch_adapter(task)
    summary = deterministic_summary(meta)
    assert "async" in summary

    fut = asyncio.Future()
    meta = dispatch_adapter(fut)
    summary = deterministic_summary(meta)
    assert "async" in summary


def test_traceback_adapter_nl() -> None:
    try:
        raise ValueError("boom")
    except ValueError as exc:
        meta = dispatch_adapter(exc.__traceback__)
    summary = deterministic_summary(meta)
    assert "traceback" in summary


networkx = pytest.importorskip("networkx")


def test_networkx_adapter_nl() -> None:
    import networkx as nx

    g = nx.Graph()
    g.add_edge("a", "b")
    meta = dispatch_adapter(g)
    summary = deterministic_summary(meta)
    assert "networkx graph" in summary


requests = pytest.importorskip("requests")


def test_requests_adapter_nl() -> None:
    import requests as rq

    resp = rq.Response()
    resp.status_code = 200
    resp.url = "https://example.com"
    meta = dispatch_adapter(resp)
    summary = deterministic_summary(meta)
    assert "HTTP response" in summary


polars = pytest.importorskip("polars")


def test_polars_adapter_nl() -> None:
    import polars as pl

    df = pl.DataFrame({"a": [1, 2], "b": ["x", "y"]})
    meta = dispatch_adapter(df)
    summary = deterministic_summary(meta)
    assert "Polars DataFrame" in summary


pydantic = pytest.importorskip("pydantic")


def test_pydantic_adapter_nl() -> None:
    from pydantic import BaseModel

    class User(BaseModel):
        name: str
        age: int

    user = User(name="alice", age=30)
    meta = dispatch_adapter(user)
    summary = deterministic_summary(meta)
    assert "Pydantic model" in summary


torch = pytest.importorskip("torch")


def test_pytorch_adapter_nl() -> None:
    import torch as t

    tensor = t.tensor([1.0, 2.0])
    meta = dispatch_adapter(tensor)
    summary = deterministic_summary(meta)
    assert "PyTorch tensor" in summary


xarray = pytest.importorskip("xarray")


def test_xarray_adapter_nl() -> None:
    import xarray as xr

    arr = xr.DataArray([[1, 2], [3, 4]], dims=["x", "y"])
    meta = dispatch_adapter(arr)
    summary = deterministic_summary(meta)
    assert "xarray object" in summary
