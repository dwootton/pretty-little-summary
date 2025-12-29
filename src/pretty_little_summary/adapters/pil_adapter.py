"""Adapter for PIL Image objects."""

from __future__ import annotations

from typing import Any

try:
    from PIL import Image
    LIBRARY_AVAILABLE = True
except ImportError:
    LIBRARY_AVAILABLE = False

from pretty_little_summary.adapters._base import AdapterRegistry
from pretty_little_summary.core import MetaDescription


class PILAdapter:
    """Adapter for PIL.Image.Image and lists of images."""

    @staticmethod
    def can_handle(obj: Any) -> bool:
        if not LIBRARY_AVAILABLE:
            return False
        try:
            if isinstance(obj, Image.Image):
                return True
            if isinstance(obj, list) and obj and all(isinstance(x, Image.Image) for x in obj[:5]):
                return True
        except Exception:
            return False
        return False

    @staticmethod
    def extract_metadata(obj: Any) -> MetaDescription:
        meta: MetaDescription = {
            "object_type": f"{type(obj).__module__}.{type(obj).__name__}",
            "adapter_used": "PILAdapter",
        }

        metadata: dict[str, Any] = {}

        try:
            if isinstance(obj, Image.Image):
                metadata.update(_describe_image(obj))
                meta["shape"] = (obj.size[1], obj.size[0])
            elif isinstance(obj, list):
                metadata.update(_describe_image_list(obj))
        except Exception as e:
            meta["warnings"] = [f"PILAdapter failed: {e}"]

        if metadata:
            meta["metadata"] = metadata
            meta["nl_summary"] = _build_nl_summary(metadata)
        return meta


def _describe_image(img: "Image.Image") -> dict[str, Any]:
    width, height = img.size
    metadata: dict[str, Any] = {
        "type": "pil_image",
        "mode": img.mode,
        "width": width,
        "height": height,
        "format": img.format,
    }
    is_animated = getattr(img, "is_animated", False)
    if is_animated:
        metadata["is_animated"] = True
        metadata["n_frames"] = getattr(img, "n_frames", None)
    return metadata


def _describe_image_list(images: list["Image.Image"]) -> dict[str, Any]:
    sizes = [img.size for img in images[:5]]
    modes = list({img.mode for img in images[:5]})
    uniform = len(set(sizes)) == 1 if sizes else False
    return {
        "type": "pil_image_list",
        "count": len(images),
        "uniform_size": uniform,
        "sample_sizes": sizes,
        "modes": modes,
    }


if LIBRARY_AVAILABLE:
    AdapterRegistry.register(PILAdapter)


def _build_nl_summary(metadata: dict[str, Any]) -> str:
    if metadata.get("type") == "pil_image":
        return (
            f"A PIL image {metadata.get('width')}x{metadata.get('height')} "
            f"in {metadata.get('mode')} mode."
        )
    if metadata.get("type") == "pil_image_list":
        return f"A list of {metadata.get('count')} PIL images."
    return "A PIL image object."
