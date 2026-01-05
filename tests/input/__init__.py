"""File-based example fixtures for tests and docs."""

from __future__ import annotations

from importlib import import_module
from pathlib import Path
from types import ModuleType
from typing import Callable, Iterable


def load_example(example_id: str) -> ModuleType:
    """Import and return the example module for the given id."""
    return import_module(f"tests.input.{example_id}")


def list_example_ids() -> list[str]:
    """Return all example ids based on files in tests/input."""
    base = Path(__file__).parent
    ids: list[str] = []
    for path in sorted(base.glob("*.py")):
        if path.name.startswith("__"):
            continue
        ids.append(path.stem)
    return ids


def iter_examples() -> Iterable[ModuleType]:
    """Yield imported example modules."""
    for example_id in list_example_ids():
        yield load_example(example_id)


def build_input(example: ModuleType, **kwargs: object) -> object:
    """Build the input object from an example module."""
    builder = getattr(example, "build", None)
    if not callable(builder):
        raise ValueError(f"Example '{example.__name__}' is missing a build() function")
    return builder(**kwargs)


def expected_output(example: ModuleType, meta: object | None = None) -> str:
    """Return the expected output for an example."""
    expected_fn = getattr(example, "expected", None)
    if callable(expected_fn):
        return expected_fn(meta)
    expected = getattr(example, "EXPECTED", None)
    if not isinstance(expected, str):
        raise ValueError(f"Example '{example.__name__}' missing EXPECTED output")
    return expected
