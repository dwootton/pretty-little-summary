"""Sklearn adapter."""

from typing import Any

# Sklearn uses duck typing, no import check needed
LIBRARY_AVAILABLE = True

from pretty_little_summary.adapters._base import AdapterRegistry
from pretty_little_summary.core import MetaDescription


class SklearnAdapter:
    """Adapter for scikit-learn models."""

    @staticmethod
    def can_handle(obj: Any) -> bool:
        if not LIBRARY_AVAILABLE:
            return False
        try:
            return hasattr(obj, 'get_params') and hasattr(obj, 'fit')
        except Exception:
            return False

    @staticmethod
    def extract_metadata(obj: Any) -> MetaDescription:
        try:
            meta: MetaDescription = {
                "object_type": f"sklearn.{obj.__class__.__name__}",
                "adapter_used": "SklearnAdapter",
            }

            # Get hyperparameters
            try:
                meta["parameters"] = obj.get_params()
            except Exception as e:
                meta.setdefault("warnings", []).append(f"Could not get params: {e}")

            # Check if fitted
            is_fitted = hasattr(obj, "n_features_in_")
            meta["is_fitted"] = is_fitted

            if is_fitted:
                try:
                    meta["metadata"] = {"n_features_in_": obj.n_features_in_}
                except Exception:
                    pass

                # Get classes if classifier
                if hasattr(obj, "classes_"):
                    try:
                        classes = obj.classes_
                        if hasattr(classes, "tolist"):
                            meta["metadata"] = meta.get("metadata", {})
                            meta["metadata"]["classes_"] = classes.tolist()
                    except Exception:
                        pass

                # Get feature names if available
                if hasattr(obj, "feature_names_in_"):
                    try:
                        feature_names = obj.feature_names_in_
                        if hasattr(feature_names, "tolist"):
                            meta["metadata"] = meta.get("metadata", {})
                            meta["metadata"]["feature_names_in_"] = feature_names.tolist()
                    except Exception:
                        pass

            meta["nl_summary"] = f"A sklearn model {meta['object_type']}."
            return meta

        except Exception as e:
            return {
                "object_type": f"{type(obj).__module__}.{type(obj).__name__}",
                "adapter_used": "SklearnAdapter (failed)",
                "warnings": [f"Adapter failed: {e}"],
                "raw_repr": repr(obj)[:500],
            }



# Auto-register if library is available
if LIBRARY_AVAILABLE:
    AdapterRegistry.register(SklearnAdapter)
