"""Polars adapter."""

from typing import Any

try:
    import polars as pl
    LIBRARY_AVAILABLE = True
except ImportError:
    LIBRARY_AVAILABLE = False

from wut_is.adapters._base import AdapterRegistry
from wut_is.core import MetaDescription


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
                    # Convert to pandas for markdown representation
                    meta["sample_data"] = obj.head(3).to_pandas().to_markdown()
                except Exception:
                    try:
                        meta["sample_data"] = str(obj.head(3))
                    except Exception as e:
                        meta.setdefault("warnings", []).append(
                            f"Could not get sample data: {e}"
                        )

            meta["nl_summary"] = f"A Polars DataFrame with shape {meta.get('shape')}."
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
