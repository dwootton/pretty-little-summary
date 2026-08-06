"""Pydantic adapter."""

from typing import Any

try:
    from pydantic import BaseModel
    LIBRARY_AVAILABLE = True
except ImportError:
    LIBRARY_AVAILABLE = False

from pretty_little_summary.adapters._base import AdapterRegistry
from pretty_little_summary.core import MetaDescription


def _build_nl_summary(meta: dict[str, Any]) -> str:
    object_type = meta.get("object_type")
    fields = list((meta.get("fields") or {}).keys())
    values = (meta.get("metadata") or {}).get("values") or {}
    shown = fields[:8]
    pairs = ", ".join(f"{name}={values.get(name)!r}" for name in shown)
    suffix = f", ... ({len(fields)} fields total)" if len(fields) > 8 else ""
    if not pairs:
        return f"A Pydantic model {object_type}."
    return f"A Pydantic model {object_type} with fields: {pairs}{suffix}."


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
                # Access model_fields on the class: reading it from the instance
                # is deprecated in Pydantic 2.11+.
                model_fields = type(obj).model_fields
                meta["fields"] = {
                    k: str(v.annotation) for k, v in model_fields.items()
                }
            except Exception as e:
                meta.setdefault("warnings", []).append(f"Could not get fields: {e}")

            # Get current values
            try:
                meta["metadata"] = {"values": obj.model_dump()}
            except Exception as e:
                meta.setdefault("warnings", []).append(f"Could not dump values: {e}")

            meta["nl_summary"] = _build_nl_summary(meta)
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
