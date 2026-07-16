"""Adapter for TensorFlow tensors."""

from __future__ import annotations

from typing import Any

from pretty_little_summary.adapters._base import AdapterRegistry, module_loaded
from pretty_little_summary.core import MetaDescription
from pretty_little_summary.descriptor_utils import safe_repr


class TensorflowAdapter:
    """Adapter for tf.Tensor objects.

    Detection is gated on tensorflow already being imported so this adapter
    never triggers tensorflow's (heavy) import on its own.
    """

    @staticmethod
    def can_handle(obj: Any) -> bool:
        if not module_loaded("tensorflow"):
            return False
        try:
            import tensorflow as tf

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


AdapterRegistry.register(TensorflowAdapter)
