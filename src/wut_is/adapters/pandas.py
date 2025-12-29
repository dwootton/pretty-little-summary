"""Pandas adapter."""

from typing import Any

try:
    import pandas as pd
    LIBRARY_AVAILABLE = True
except ImportError:
    LIBRARY_AVAILABLE = False

from wut_is.adapters._base import AdapterRegistry
from wut_is.core import MetaDescription


class PandasAdapter:
    """Adapter for pandas DataFrame/Series."""

    @staticmethod
    def can_handle(obj: Any) -> bool:
        if not LIBRARY_AVAILABLE:
            return False
        try:
            return isinstance(obj, (pd.DataFrame, pd.Series))
        except Exception:
            return False

    @staticmethod
    def extract_metadata(obj: Any) -> MetaDescription:
        try:
            import pandas as pd

            meta: MetaDescription = {
                "object_type": f"pandas.{type(obj).__name__}",
                "adapter_used": "PandasAdapter",
            }

            # Shape
            try:
                meta["shape"] = obj.shape
            except Exception as e:
                meta.setdefault("warnings", []).append(f"Could not get shape: {e}")

            # Columns (DataFrame only)
            if isinstance(obj, pd.DataFrame):
                try:
                    meta["columns"] = obj.columns.tolist()
                except Exception as e:
                    meta.setdefault("warnings", []).append(f"Could not get columns: {e}")

                # Dtypes
                try:
                    meta["dtypes"] = {col: str(dtype) for col, dtype in obj.dtypes.items()}
                except Exception as e:
                    meta.setdefault("warnings", []).append(f"Could not get dtypes: {e}")

                # Sample data (first 3 rows as markdown)
                try:
                    meta["sample_data"] = obj.head(3).to_markdown()
                except Exception:
                    # to_markdown might not be available
                    try:
                        meta["sample_data"] = obj.head(3).to_string()
                    except Exception as e:
                        meta.setdefault("warnings", []).append(
                            f"Could not get sample data: {e}"
                        )
            else:
                # Series
                try:
                    meta["dtypes"] = {"dtype": str(obj.dtype)}
                except Exception as e:
                    meta.setdefault("warnings", []).append(f"Could not get dtype: {e}")

            return meta

        except Exception as e:
            # Fallback to generic if adapter completely fails
            return {
                "object_type": f"{type(obj).__module__}.{type(obj).__name__}",
                "adapter_used": "PandasAdapter (failed)",
                "warnings": [f"Adapter failed: {e}"],
                "raw_repr": repr(obj)[:500],
            }



# Auto-register if library is available
if LIBRARY_AVAILABLE:
    AdapterRegistry.register(PandasAdapter)
