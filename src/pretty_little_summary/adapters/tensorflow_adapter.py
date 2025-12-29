"""Adapter for TensorFlow tensors."""

from __future__ import annotations

from typing import Any

try:
    import tensorflow as tf
    LIBRARY_AVAILABLE = True
except ImportError:
    LIBRARY_AVAILABLE = False

from pretty_little_summary.adapters._base import AdapterRegistry
from pretty_little_summary.core import MetaDescription
from pretty_little_summary.descriptor_utils import safe_repr


class TensorflowAdapter:
    """Adapter for tf.Tensor objects."""

    @staticmethod
    def can_handle(obj: Any) -> bool:
        if not LIBRARY_AVAILABLE:
            return False
        try:
            return isinstance(obj, tf.Tensor)
        except Exception:
            return False

    @staticmethod
    def extract_metadata(obj: Any) -> MetaDescription:
        meta: MetaDescription = {
            "object_type": f"{type(obj).__module__}.{type(obj).__name__}",
            "adapter_used": "TensorflowAdapter",
        }
        metadata: dict[str, Any] = {
            "type": "tf_tensor",
            "shape": tuple(obj.shape),
            "dtype": str(obj.dtype),
            "device": getattr(obj, "device", None),
        }
        try:
            if obj.shape and obj.shape.num_elements() and obj.shape.num_elements() <= 10:
                metadata["sample_values"] = safe_repr(obj.numpy().tolist(), 100)
        except Exception:
            pass

        meta["metadata"] = metadata
        meta["nl_summary"] = f"A TensorFlow tensor with shape {metadata.get('shape')}."
        return meta


if LIBRARY_AVAILABLE:
    AdapterRegistry.register(TensorflowAdapter)
