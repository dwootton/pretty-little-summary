"""Adapter for statsmodels results objects."""

from __future__ import annotations

from typing import Any

from pretty_little_summary.adapters._base import AdapterRegistry
from pretty_little_summary.core import MetaDescription


class StatsmodelsAdapter:
    """Adapter for statsmodels result objects."""

    @staticmethod
    def can_handle(obj: Any) -> bool:
        module = type(obj).__module__
        return "statsmodels" in module and (hasattr(obj, "params") or hasattr(obj, "summary"))

    @staticmethod
    def extract_metadata(obj: Any) -> MetaDescription:
        meta: MetaDescription = {
            "object_type": f"{type(obj).__module__}.{type(obj).__name__}",
            "adapter_used": "StatsmodelsAdapter",
        }
        metadata: dict[str, Any] = {"type": "statsmodels_result"}
        try:
            metadata["model_type"] = type(obj).__name__
            if hasattr(obj, "params"):
                params = obj.params
                metadata["param_count"] = len(params)
            if hasattr(obj, "rsquared"):
                metadata["rsquared"] = float(obj.rsquared)
        except Exception:
            pass

        meta["metadata"] = metadata
        meta["nl_summary"] = _build_nl_summary(metadata)
        return meta


AdapterRegistry.register(StatsmodelsAdapter)


def _build_nl_summary(metadata: dict[str, Any]) -> str:
    return f"A statsmodels results object {metadata.get('model_type')}."
