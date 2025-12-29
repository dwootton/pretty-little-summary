"""Altair adapter."""

from typing import Any

try:
    import altair
    LIBRARY_AVAILABLE = True
except ImportError:
    LIBRARY_AVAILABLE = False

from pretty_little_summary.adapters._base import AdapterRegistry
from pretty_little_summary.core import MetaDescription


class AltairAdapter:
    """Adapter for Altair/Vega-Lite charts."""

    @staticmethod
    def can_handle(obj: Any) -> bool:
        if not LIBRARY_AVAILABLE:
            return False
        try:
            return isinstance(
                obj,
                (
                    altair.Chart,
                    altair.LayerChart,
                    altair.FacetChart,
                    altair.HConcatChart,
                    altair.VConcatChart,
                ),
            )
        except Exception:
            return False

    @staticmethod
    def extract_metadata(obj: Any) -> MetaDescription:
        try:
            meta: MetaDescription = {
                "object_type": f"{type(obj).__module__}.{type(obj).__name__}",
                "adapter_used": "AltairAdapter",
            }

            # Extract spec and strip data
            try:
                spec = obj.to_dict()
                spec_stripped = AltairAdapter._strip_data(spec)
                meta["spec"] = spec_stripped

                # Extract key fields
                meta["chart_type"] = spec_stripped.get("mark")
                meta["metadata"] = meta.get("metadata", {})
                if "encoding" in spec_stripped:
                    meta["metadata"]["encoding"] = spec_stripped["encoding"]
                if "transform" in spec_stripped:
                    meta["metadata"]["transform"] = spec_stripped["transform"]
                if "layer" in spec_stripped:
                    meta["metadata"]["layer_count"] = len(spec_stripped["layer"])
            except Exception as e:
                meta.setdefault("warnings", []).append(f"Could not extract spec: {e}")

            meta["nl_summary"] = _build_nl_summary(meta)
            return meta

        except Exception as e:
            return {
                "object_type": f"{type(obj).__module__}.{type(obj).__name__}",
                "adapter_used": "AltairAdapter (failed)",
                "warnings": [f"Adapter failed: {e}"],
                "raw_repr": repr(obj)[:500],
            }

    @staticmethod
    def _strip_data(spec: dict[str, Any]) -> dict[str, Any]:
        """Remove large data arrays, keep first 2 rows as sample."""
        import copy

        spec_copy = copy.deepcopy(spec)
        if "data" in spec_copy and isinstance(spec_copy["data"], dict):
            if "values" in spec_copy["data"] and isinstance(spec_copy["data"]["values"], list):
                spec_copy["data"]["values"] = spec_copy["data"]["values"][:2]
        return spec_copy



# Auto-register if library is available
if LIBRARY_AVAILABLE:
    AdapterRegistry.register(AltairAdapter)


def _build_nl_summary(meta: MetaDescription) -> str:
    mark = meta.get("chart_type") or "unknown"
    return f"An Altair chart with mark '{mark}'."
