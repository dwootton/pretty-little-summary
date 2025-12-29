"""Adapter for h5py Dataset objects."""

from __future__ import annotations

from typing import Any

try:
    import h5py
    LIBRARY_AVAILABLE = True
except ImportError:
    LIBRARY_AVAILABLE = False

from wut_is.adapters._base import AdapterRegistry
from wut_is.core import MetaDescription
from wut_is.descriptor_utils import safe_repr


class H5pyAdapter:
    """Adapter for h5py.Dataset."""

    @staticmethod
    def can_handle(obj: Any) -> bool:
        if not LIBRARY_AVAILABLE:
            return False
        try:
            return isinstance(obj, h5py.Dataset)
        except Exception:
            return False

    @staticmethod
    def extract_metadata(obj: Any) -> MetaDescription:
        meta: MetaDescription = {
            "object_type": f"{type(obj).__module__}.{type(obj).__name__}",
            "adapter_used": "H5pyAdapter",
        }
        metadata: dict[str, Any] = {}
        try:
            metadata.update(_describe_dataset(obj))
            meta["shape"] = obj.shape
        except Exception as e:
            meta["warnings"] = [f"H5pyAdapter failed: {e}"]

        if metadata:
            meta["metadata"] = metadata
        return meta


def _describe_dataset(dataset: "h5py.Dataset") -> dict[str, Any]:
    attrs = {k: safe_repr(v, 100) for k, v in dataset.attrs.items()}
    sample = None
    try:
        if dataset.shape and dataset.shape[0] > 0:
            sample = safe_repr(dataset[0], 100)
    except Exception:
        sample = None

    return {
        "type": "h5py_dataset",
        "name": dataset.name,
        "dtype": str(dataset.dtype),
        "chunks": dataset.chunks,
        "compression": dataset.compression,
        "attrs": attrs,
        "sample": sample,
    }


if LIBRARY_AVAILABLE:
    AdapterRegistry.register(H5pyAdapter)
