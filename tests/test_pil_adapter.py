"""Tests for PIL adapter."""

import pytest

from wut_is.adapters import dispatch_adapter


pil = pytest.importorskip("PIL")
from PIL import Image  # noqa: E402


def test_pil_image_adapter() -> None:
    img = Image.new("RGB", (64, 32))
    meta = dispatch_adapter(img)
    assert meta["adapter_used"] == "PILAdapter"
    assert meta["metadata"]["type"] == "pil_image"
    assert meta["metadata"]["width"] == 64


def test_pil_image_list_adapter() -> None:
    imgs = [Image.new("RGB", (32, 32)) for _ in range(3)]
    meta = dispatch_adapter(imgs)
    assert meta["metadata"]["type"] == "pil_image_list"
    assert meta["metadata"]["count"] == 3
