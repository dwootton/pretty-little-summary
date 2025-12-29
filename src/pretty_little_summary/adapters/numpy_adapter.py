"""Adapter for NumPy arrays and scalars."""

from __future__ import annotations

from typing import Any

try:
    import numpy as np
    LIBRARY_AVAILABLE = True
except ImportError:
    LIBRARY_AVAILABLE = False

from pretty_little_summary.adapters._base import AdapterRegistry
from pretty_little_summary.core import MetaDescription
from pretty_little_summary.descriptor_utils import compute_numeric_stats, format_bytes, safe_repr


class NumpyAdapter:
    """Adapter for numpy.ndarray and numpy scalar types."""

    @staticmethod
    def can_handle(obj: Any) -> bool:
        if not LIBRARY_AVAILABLE:
            return False
        try:
            return isinstance(obj, (np.ndarray, np.generic))
        except Exception:
            return False

    @staticmethod
    def extract_metadata(obj: Any) -> MetaDescription:
        from pretty_little_summary.descriptor_registry import DescribeConfigRegistry

        config = DescribeConfigRegistry.get()
        meta: MetaDescription = {
            "object_type": "numpy.ndarray" if hasattr(obj, "shape") else "numpy.scalar",
            "adapter_used": "NumpyAdapter",
        }
        metadata: dict[str, Any] = {}

        try:
            import numpy as np

            if isinstance(obj, np.ndarray):
                metadata.update(_describe_ndarray(obj, config))
                meta["shape"] = obj.shape
            else:
                metadata.update(_describe_scalar(obj))
        except Exception as e:
            meta["warnings"] = [f"NumpyAdapter failed: {e}"]

        if metadata:
            meta["metadata"] = metadata
            meta["nl_summary"] = _build_nl_summary(metadata, meta.get("shape"))
        return meta


def _describe_ndarray(arr: "np.ndarray", config) -> dict[str, Any]:
    metadata: dict[str, Any] = {
        "type": "ndarray",
        "dtype": str(arr.dtype),
        "ndim": int(arr.ndim),
        "size": int(arr.size),
        "nbytes": int(arr.nbytes),
        "memory": format_bytes(int(arr.nbytes)),
    }

    include_samples = arr.size <= config.max_sample_elements
    if arr.ndim == 1 and include_samples:
        metadata["shape"] = (int(arr.shape[0]),)
        metadata["sample_start"] = [safe_repr(v, 50) for v in arr[:5].tolist()]
        metadata["sample_end"] = [safe_repr(v, 50) for v in arr[-5:].tolist()]
    elif arr.ndim == 2 and include_samples:
        metadata["shape"] = (int(arr.shape[0]), int(arr.shape[1]))
        metadata["sample_corner"] = arr[:3, :3].tolist()
    else:
        metadata["shape"] = tuple(int(x) for x in arr.shape)

    if _is_numeric_dtype(arr.dtype):
        stats = compute_numeric_stats(_sample_numeric_array(arr, 10000))
        if stats:
            metadata["stats"] = stats.to_prose()

    return metadata


def _describe_scalar(value: "np.generic") -> dict[str, Any]:
    return {
        "type": "numpy_scalar",
        "dtype": str(value.dtype),
        "value": safe_repr(value.item(), 50),
        "itemsize": int(value.itemsize),
    }


def _sample_numeric_array(arr: "np.ndarray", limit: int) -> list[float | int]:
    flat = arr.ravel()
    if flat.size > limit:
        sample = flat[:limit]
    else:
        sample = flat
    return [float(v) if hasattr(v, "__float__") else int(v) for v in sample.tolist()]


def _is_numeric_dtype(dtype: "np.dtype") -> bool:
    return dtype.kind in {"i", "u", "f"}


if LIBRARY_AVAILABLE:
    AdapterRegistry.register(NumpyAdapter)


def _build_nl_summary(metadata: dict[str, Any], shape: Any) -> str:
    if metadata.get("type") == "ndarray":
        parts = [
            f"A numpy array with shape {metadata.get('shape', shape)} and dtype {metadata.get('dtype')}."
        ]
        sample_start = metadata.get("sample_start")
        sample_end = metadata.get("sample_end")
        sample_corner = metadata.get("sample_corner")
        if sample_corner is not None:
            parts.append(f"Sample corner: {sample_corner}.")
        elif sample_start is not None:
            if sample_end and sample_end != sample_start:
                parts.append(f"Sample: [{', '.join(sample_start)} ... {', '.join(sample_end)}].")
            else:
                parts.append(f"Sample: [{', '.join(sample_start)}].")
        return " ".join(parts)
    if metadata.get("type") == "numpy_scalar":
        return (
            f"A numpy {metadata.get('dtype')} scalar with value {metadata.get('value')}."
        )
    return "A numpy object."
