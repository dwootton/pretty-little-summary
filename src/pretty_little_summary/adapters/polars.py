"""Polars adapter."""

from typing import Any

try:
    import polars as pl
    LIBRARY_AVAILABLE = True
except ImportError:
    LIBRARY_AVAILABLE = False

from pretty_little_summary.adapters._base import AdapterRegistry
from pretty_little_summary.core import MetaDescription
from pretty_little_summary.descriptor_registry import DescribeConfigRegistry
from pretty_little_summary.descriptor_utils import safe_repr


class PolarsAdapter:
    """Adapter for Polars DataFrame/LazyFrame."""

    @staticmethod
    def can_handle(obj: Any) -> bool:
        if not LIBRARY_AVAILABLE:
            return False
        try:
            return isinstance(obj, (pl.DataFrame, pl.LazyFrame))
        except Exception:
            return False

    @staticmethod
    def extract_metadata(obj: Any) -> MetaDescription:
        try:
            import polars as pl

            is_lazy = isinstance(obj, pl.LazyFrame)
            config = DescribeConfigRegistry.get()

            meta: MetaDescription = {
                "object_type": "polars.LazyFrame" if is_lazy else "polars.DataFrame",
                "adapter_used": "PolarsAdapter",
            }

            # Schema (available for both Lazy and Eager)
            try:
                meta["schema"] = {k: str(v) for k, v in obj.schema.items()}
            except Exception as e:
                meta.setdefault("warnings", []).append(f"Could not get schema: {e}")

            if is_lazy:
                # For lazy frames, get optimized plan
                try:
                    meta["metadata"] = {"optimized_plan": obj.explain()}
                except Exception as e:
                    meta.setdefault("warnings", []).append(
                        f"Could not get optimized plan: {e}"
                    )
            else:
                # For eager frames, get shape and sample data
                try:
                    meta["shape"] = obj.shape
                except Exception as e:
                    meta.setdefault("warnings", []).append(f"Could not get shape: {e}")

                try:
                    rows, cols = obj.shape
                    if rows * cols <= config.max_sample_cells and rows <= config.max_sample_rows:
                        sample = obj.head(config.sample_size).to_dicts()
                        meta["metadata"] = meta.get("metadata", {})
                        meta["metadata"]["sample_rows"] = [
                            {str(k): safe_repr(v, config.max_sample_repr) for k, v in row.items()}
                            for row in sample
                        ]
                    else:
                        meta["metadata"] = meta.get("metadata", {})
                        meta["metadata"]["sample_rows_omitted"] = True
                except Exception:
                    pass

            meta["nl_summary"] = _build_nl_summary(meta)
            return meta

        except Exception as e:
            return {
                "object_type": f"{type(obj).__module__}.{type(obj).__name__}",
                "adapter_used": "PolarsAdapter (failed)",
                "warnings": [f"Adapter failed: {e}"],
                "raw_repr": repr(obj)[:500],
            }



# Auto-register if library is available
if LIBRARY_AVAILABLE:
    AdapterRegistry.register(PolarsAdapter)


def _build_nl_summary(meta: MetaDescription) -> str:
    shape = meta.get("shape")
    schema = meta.get("schema") or {}
    parts = [f"A Polars DataFrame with shape {shape}."]
    if schema:
        cols = []
        for name, dtype in list(schema.items())[:3]:
            cols.append(f"{name} ({dtype})")
        if cols:
            parts.append(f"Schema: {', '.join(cols)}.")
    sample_rows = meta.get("metadata", {}).get("sample_rows")
    if sample_rows:
        parts.append(f"Sample row: {sample_rows[0]}.")
    elif meta.get("metadata", {}).get("sample_rows_omitted"):
        parts.append("Sample rows omitted for size/perf.")
    return " ".join(parts)
