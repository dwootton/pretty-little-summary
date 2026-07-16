"""Adapter for JAX arrays."""

from __future__ import annotations

from typing import Any

from pretty_little_summary.adapters._base import AdapterRegistry, module_loaded
from pretty_little_summary.core import MetaDescription


class JaxAdapter:
    """Adapter for JAX array objects.

    Detection is gated on jax already being imported so this adapter never
    triggers jax's (heavy) import on its own.
    """

    @staticmethod
    def can_handle(obj: Any) -> bool:
        if not module_loaded("jax"):
            return False
        try:
            import jax

            return isinstance(obj, jax.Array)
        except Exception:
            return False

    @staticmethod
    def extract_metadata(obj: Any) -> MetaDescription:
        meta: MetaDescription = {
            "object_type": f"{type(obj).__module__}.{type(obj).__name__}",
            "adapter_used": "JaxAdapter",
        }
        metadata: dict[str, Any] = {
            "type": "jax_array",
            "shape": tuple(obj.shape),
            "dtype": str(obj.dtype),
        }
        meta["metadata"] = metadata
        meta["nl_summary"] = f"A JAX array with shape {metadata.get('shape')}."
        return meta


AdapterRegistry.register(JaxAdapter)
