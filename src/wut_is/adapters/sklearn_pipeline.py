"""Adapter for scikit-learn Pipeline objects."""

from __future__ import annotations

from typing import Any

from wut_is.adapters._base import AdapterRegistry
from wut_is.core import MetaDescription


class SklearnPipelineAdapter:
    """Adapter for sklearn.pipeline.Pipeline."""

    @staticmethod
    def can_handle(obj: Any) -> bool:
        return hasattr(obj, "steps") and isinstance(getattr(obj, "steps", None), list)

    @staticmethod
    def extract_metadata(obj: Any) -> MetaDescription:
        meta: MetaDescription = {
            "object_type": f"{type(obj).__module__}.{type(obj).__name__}",
            "adapter_used": "SklearnPipelineAdapter",
        }
        metadata: dict[str, Any] = {"type": "sklearn_pipeline"}
        try:
            steps = []
            for name, step in obj.steps:
                steps.append({"name": name, "class": step.__class__.__name__})
            metadata["steps"] = steps
            metadata["step_count"] = len(steps)
        except Exception:
            pass

        try:
            metadata["is_fitted"] = hasattr(obj, "n_features_in_")
        except Exception:
            pass

        meta["metadata"] = metadata
        return meta


AdapterRegistry.register(SklearnPipelineAdapter)
