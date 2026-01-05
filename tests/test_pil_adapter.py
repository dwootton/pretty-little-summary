"""Tests for PIL adapter."""

import pytest

from pretty_little_summary.adapters import dispatch_adapter
from pretty_little_summary.synthesizer import deterministic_summary
from tests.input import build_input, expected_output, load_example


pil = pytest.importorskip("PIL")


def test_pil_image_adapter() -> None:
    example = load_example("pil_image_adapter")
    meta = dispatch_adapter(build_input(example))
    assert meta["adapter_used"] == "PILAdapter"
    assert meta["metadata"]["type"] == "pil_image"
    assert meta["metadata"]["width"] == 64
    summary = deterministic_summary(meta)
    print("pil_image:", summary)
    assert summary == expected_output(example, meta)


def test_pil_image_list_adapter() -> None:
    example = load_example("pil_image_list_adapter")
    meta = dispatch_adapter(build_input(example))
    assert meta["metadata"]["type"] == "pil_image_list"
    assert meta["metadata"]["count"] == 3
    summary = deterministic_summary(meta)
    print("pil_list:", summary)
    assert summary == expected_output(example, meta)
