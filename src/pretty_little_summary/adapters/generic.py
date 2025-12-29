"""Generic fallback adapter for unknown types."""

from typing import Any

from pretty_little_summary.adapters._base import Adapter, AdapterRegistry
from pretty_little_summary.core import MetaDescription


class GenericAdapter:
    """Fallback adapter for unknown types."""

    @staticmethod
    def can_handle(obj: Any) -> bool:
        return True  # Always handles (lowest priority)

    @staticmethod
    def extract_metadata(obj: Any) -> MetaDescription:
        obj_type = type(obj)
        type_name = obj_type.__name__
        module_name = obj_type.__module__

        meta: MetaDescription = {
            "object_type": f"{module_name}.{type_name}",
            "adapter_used": "GenericAdapter",
        }

        # Enhanced metadata for built-in types
        metadata: dict[str, Any] = {}

        # Dict
        if isinstance(obj, dict):
            metadata["length"] = len(obj)
            if obj:
                metadata["keys"] = list(obj.keys())[:10]
                metadata["sample_items"] = {k: type(v).__name__ for k, v in list(obj.items())[:5]}

        # List/Tuple
        elif isinstance(obj, (list, tuple)):
            metadata["length"] = len(obj)
            if obj:
                metadata["element_types"] = list(set(type(x).__name__ for x in obj[:20]))
                metadata["sample_items"] = [repr(x)[:50] for x in obj[:5]]

        # Set
        elif isinstance(obj, set):
            metadata["length"] = len(obj)
            if obj:
                metadata["element_types"] = list(set(type(x).__name__ for x in list(obj)[:20]))

        # String
        elif isinstance(obj, str):
            metadata["length"] = len(obj)
            metadata["preview"] = obj[:100]

        # Numeric types
        elif isinstance(obj, (int, float, complex)):
            metadata["value"] = str(obj)

        # Boolean
        elif isinstance(obj, bool):
            metadata["value"] = str(obj)

        # None
        elif obj is None:
            metadata["value"] = "None"

        # Try to get repr for everything
        try:
            meta["raw_repr"] = repr(obj)[:1000]
        except Exception:
            meta["raw_repr"] = f"<{type_name} object>"

        # Try to get non-private attributes for custom objects
        try:
            attrs = [a for a in dir(obj) if not a.startswith("_")][:20]
            if attrs and not isinstance(obj, (dict, list, tuple, set, str, int, float, complex, bool, type(None))):
                metadata["attributes"] = attrs
        except Exception:
            pass

        if metadata:
            meta["metadata"] = metadata

        meta["nl_summary"] = f"An object of type {meta['object_type']}."
        return meta


# Always register GenericAdapter (lowest priority)
AdapterRegistry.register(GenericAdapter)
