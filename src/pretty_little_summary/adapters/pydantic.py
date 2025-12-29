"""Pydantic adapter."""

from typing import Any

try:
    from pydantic import BaseModel
    LIBRARY_AVAILABLE = True
except ImportError:
    LIBRARY_AVAILABLE = False

from pretty_little_summary.adapters._base import AdapterRegistry
from pretty_little_summary.core import MetaDescription


class PydanticAdapter:
    """Adapter for Pydantic BaseModel."""

    @staticmethod
    def can_handle(obj: Any) -> bool:
        if not LIBRARY_AVAILABLE:
            return False
        try:
            return isinstance(obj, BaseModel)
        except Exception:
            return False

    @staticmethod
    def extract_metadata(obj: Any) -> MetaDescription:
        try:
            meta: MetaDescription = {
                "object_type": f"pydantic.{obj.__class__.__name__}",
                "adapter_used": "PydanticAdapter",
            }

            # Get JSON schema
            try:
                meta["schema"] = obj.model_json_schema()
            except Exception as e:
                meta.setdefault("warnings", []).append(f"Could not get schema: {e}")

            # Get field info
            try:
                meta["fields"] = {
                    k: str(v.annotation) for k, v in obj.model_fields.items()
                }
            except Exception as e:
                meta.setdefault("warnings", []).append(f"Could not get fields: {e}")

            # Get current values
            try:
                meta["metadata"] = {"values": obj.model_dump()}
            except Exception as e:
                meta.setdefault("warnings", []).append(f"Could not dump values: {e}")

            meta["nl_summary"] = f"A Pydantic model {meta['object_type']}."
            return meta

        except Exception as e:
            return {
                "object_type": f"{type(obj).__module__}.{type(obj).__name__}",
                "adapter_used": "PydanticAdapter (failed)",
                "warnings": [f"Adapter failed: {e}"],
                "raw_repr": repr(obj)[:500],
            }



# Auto-register if library is available
if LIBRARY_AVAILABLE:
    AdapterRegistry.register(PydanticAdapter)
