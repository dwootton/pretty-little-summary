"""Adapters for async-related objects."""

from __future__ import annotations

import asyncio
import inspect
from typing import Any

from pretty_little_summary.adapters._base import AdapterRegistry
from pretty_little_summary.core import MetaDescription


class AsyncAdapter:
    """Adapter for coroutine, Task, and Future objects."""

    @staticmethod
    def can_handle(obj: Any) -> bool:
        if inspect.iscoroutine(obj):
            return True
        if isinstance(obj, asyncio.Task):
            return True
        if isinstance(obj, asyncio.Future):
            return True
        return False

    @staticmethod
    def extract_metadata(obj: Any) -> MetaDescription:
        meta: MetaDescription = {
            "object_type": f"{type(obj).__module__}.{type(obj).__name__}",
            "adapter_used": "AsyncAdapter",
        }
        metadata: dict[str, Any] = {}

        if inspect.iscoroutine(obj):
            metadata.update(_describe_coroutine(obj))
        elif isinstance(obj, asyncio.Task):
            metadata.update(_describe_task(obj))
        elif isinstance(obj, asyncio.Future):
            metadata.update(_describe_future(obj))

        if metadata:
            meta["metadata"] = metadata
            meta["nl_summary"] = _build_nl_summary(metadata)
        return meta


def _describe_coroutine(obj: Any) -> dict[str, Any]:
    state = "closed"
    if obj.cr_running:
        state = "running"
    elif obj.cr_frame is not None:
        state = "suspended"
    return {
        "type": "coroutine",
        "name": obj.cr_code.co_name,
        "qualname": obj.cr_code.co_qualname,
        "state": state,
    }


def _describe_task(task: asyncio.Task) -> dict[str, Any]:
    return {
        "type": "task",
        "name": task.get_name(),
        "done": task.done(),
        "cancelled": task.cancelled(),
        "state": _task_state(task),
        "coro_name": task.get_coro().__name__,
    }


def _describe_future(future: asyncio.Future) -> dict[str, Any]:
    return {
        "type": "future",
        "done": future.done(),
        "cancelled": future.cancelled(),
        "state": _future_state(future),
    }


def _task_state(task: asyncio.Task) -> str:
    if task.cancelled():
        return "cancelled"
    if task.done():
        return "done"
    return "pending"


def _future_state(future: asyncio.Future) -> str:
    if future.cancelled():
        return "cancelled"
    if future.done():
        return "done"
    return "pending"


AdapterRegistry.register(AsyncAdapter)


def _build_nl_summary(metadata: dict[str, Any]) -> str:
    return f"An async {metadata.get('type')} in state {metadata.get('state')}."
