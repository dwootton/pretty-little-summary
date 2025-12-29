"""Adapter for JAX arrays."""

from __future__ import annotations

from typing import Any

try:
    import jax
    import jax.numpy as jnp
    LIBRARY_AVAILABLE = True
except ImportError:
    LIBRARY_AVAILABLE = False

from pretty_little_summary.adapters._base import AdapterRegistry
from pretty_little_summary.core import MetaDescription


class JaxAdapter:
    """Adapter for JAX array objects."""

    @staticmethod
    def can_handle(obj: Any) -> bool:
        if not LIBRARY_AVAILABLE:
            return False
        try:
            return isinstance(obj, jax.Array) or isinstance(obj, jnp.ndarray)
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


if LIBRARY_AVAILABLE:
    AdapterRegistry.register(JaxAdapter)
