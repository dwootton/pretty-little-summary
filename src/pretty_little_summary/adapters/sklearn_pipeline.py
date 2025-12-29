"""Adapter for scikit-learn Pipeline objects."""

from __future__ import annotations

from typing import Any

from pretty_little_summary.adapters._base import AdapterRegistry
from pretty_little_summary.core import MetaDescription


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
        meta["nl_summary"] = _build_nl_summary(metadata)
        return meta


AdapterRegistry.register(SklearnPipelineAdapter)


def _build_nl_summary(metadata: dict[str, Any]) -> str:
    steps = metadata.get("steps", [])
    fitted = metadata.get("is_fitted")
    fit_label = "fitted" if fitted else "unfitted"
    parts = [f"A {fit_label} sklearn Pipeline with {len(steps)} steps:"]
    for idx, step in enumerate(steps, start=1):
        parts.append(f"{idx}. '{step['name']}': {step['class']}")
    parts.append("Expects input shape (*, ?), outputs class predictions.")
    return "\n".join(parts)
