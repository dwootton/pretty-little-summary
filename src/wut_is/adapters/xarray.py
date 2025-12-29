"""Xarray adapter."""

from typing import Any

try:
    import xarray as xr
    LIBRARY_AVAILABLE = True
except ImportError:
    LIBRARY_AVAILABLE = False

from wut_is.adapters._base import AdapterRegistry
from wut_is.core import MetaDescription


class XarrayAdapter:
    """Adapter for Xarray DataArray/Dataset."""

    @staticmethod
    def can_handle(obj: Any) -> bool:
        if not LIBRARY_AVAILABLE:
            return False
        try:
            return isinstance(obj, (xr.DataArray, xr.Dataset))
        except Exception:
            return False

    @staticmethod
    def extract_metadata(obj: Any) -> MetaDescription:
        try:
            import xarray as xr

            is_dataset = isinstance(obj, xr.Dataset)

            meta: MetaDescription = {
                "object_type": "xarray.Dataset" if is_dataset else "xarray.DataArray",
                "adapter_used": "XarrayAdapter",
            }

            # Dimensions
            try:
                if is_dataset:
                    # For Dataset, get dims from data_vars
                    dims_info = {}
                    for var_name, var in obj.data_vars.items():
                        dims_info[var_name] = dict(var.dims)
                    meta["metadata"] = {"dimensions": dims_info}
                else:
                    # For DataArray
                    meta["metadata"] = {"dimensions": dict(obj.dims)}
            except Exception as e:
                meta.setdefault("warnings", []).append(f"Could not get dimensions: {e}")

            # Coordinates
            try:
                meta["metadata"] = meta.get("metadata", {})
                meta["metadata"]["coordinates"] = list(obj.coords.keys())
            except Exception as e:
                meta.setdefault("warnings", []).append(f"Could not get coordinates: {e}")

            # Attributes (user-defined metadata)
            try:
                if obj.attrs:
                    meta["metadata"] = meta.get("metadata", {})
                    meta["metadata"]["attrs"] = obj.attrs
            except Exception as e:
                meta.setdefault("warnings", []).append(f"Could not get attrs: {e}")

            # Data variables (Dataset only)
            if is_dataset:
                try:
                    meta["metadata"] = meta.get("metadata", {})
                    meta["metadata"]["data_vars"] = list(obj.data_vars.keys())
                except Exception as e:
                    meta.setdefault("warnings", []).append(f"Could not get data_vars: {e}")

            try:
                meta["shape"] = obj.shape
            except Exception:
                pass

            meta["nl_summary"] = (
                f"An xarray object {meta['object_type']} with shape {meta.get('shape')}."
            )
            return meta

        except Exception as e:
            return {
                "object_type": f"{type(obj).__module__}.{type(obj).__name__}",
                "adapter_used": "XarrayAdapter (failed)",
                "warnings": [f"Adapter failed: {e}"],
                "raw_repr": repr(obj)[:500],
            }



# Auto-register if library is available
if LIBRARY_AVAILABLE:
    AdapterRegistry.register(XarrayAdapter)
