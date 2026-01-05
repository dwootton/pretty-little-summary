"""Tests for input/output example gallery fixtures."""

from __future__ import annotations

import importlib.util

import pytest

import pretty_little_summary as pls
from tests.input import build_input, expected_output, list_example_ids, load_example


def _missing_dependency(example) -> str | None:
    for module in getattr(example, "REQUIRES", []):
        if importlib.util.find_spec(module) is None:
            return module
    return None


def _example_params():
    params: list[object] = []
    for example_id in list_example_ids():
        example = load_example(example_id)
        if getattr(example, "REQUIRES_TMP_PATH", False):
            params.append(
                pytest.param(
                    example_id,
                    marks=pytest.mark.skip(reason="Requires tmp_path fixture"),
                )
            )
            continue
        missing = _missing_dependency(example)
        if missing:
            params.append(
                pytest.param(
                    example_id,
                    marks=pytest.mark.skip(reason=f"Missing dependency: {missing}"),
                )
            )
            continue
        params.append(pytest.param(example_id, id=example_id))
    return params


@pytest.mark.parametrize("example_id", _example_params())
def test_example_gallery_outputs(example_id: str) -> None:
    example = load_example(example_id)
    obj = build_input(example)
    cleanup = None
    if isinstance(obj, tuple) and len(obj) == 2:
        obj, cleanup = obj
    result = pls.describe(obj)
    assert result.content == expected_output(example, result.meta)
    if cleanup is not None:
        if hasattr(cleanup, "close"):
            cleanup.close()
        elif callable(cleanup):
            cleanup()
