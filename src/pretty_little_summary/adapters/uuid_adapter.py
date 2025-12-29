"""Adapter for UUID objects."""

from __future__ import annotations

import uuid
from typing import Any

from pretty_little_summary.adapters._base import AdapterRegistry
from pretty_little_summary.core import MetaDescription


class UUIDAdapter:
    """Adapter for uuid.UUID objects."""

    @staticmethod
    def can_handle(obj: Any) -> bool:
        return isinstance(obj, uuid.UUID)

    @staticmethod
    def extract_metadata(obj: Any) -> MetaDescription:
        meta: MetaDescription = {
            "object_type": f"{type(obj).__module__}.{type(obj).__name__}",
            "adapter_used": "UUIDAdapter",
        }
        metadata: dict[str, Any] = {
            "type": "uuid",
            "value": str(obj),
            "version": obj.version,
            "variant": obj.variant,
            "hex": obj.hex,
        }
        meta["metadata"] = metadata
        meta["nl_summary"] = f"A UUID (version {obj.version}): {metadata['value']}."
        return meta


AdapterRegistry.register(UUIDAdapter)
