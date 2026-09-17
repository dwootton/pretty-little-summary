"""Adapter for h5py Dataset objects."""

from __future__ import annotations

from typing import Any

try:
    import h5py
    LIBRARY_AVAILABLE = True
except ImportError:
    LIBRARY_AVAILABLE = False

from pretty_little_summary.adapters._base import AdapterRegistry
from pretty_little_summary.core import MetaDescription
from pretty_little_summary.descriptor_utils import safe_repr


class H5pyAdapter:
    """Adapter for HDF5 datasets, files, and groups."""

    @staticmethod
    def can_handle(obj: Any) -> bool:
        if not LIBRARY_AVAILABLE:
            return False
        try:
            return isinstance(obj, (h5py.Dataset, h5py.File, h5py.Group))
        except Exception:
            return False

    @staticmethod
    def extract_metadata(obj: Any) -> MetaDescription:
        meta: MetaDescription = {
            "object_type": f"{type(obj).__module__}.{type(obj).__name__}",
            "adapter_used": "H5pyAdapter",
        }
        metadata: dict[str, Any] = {}
        try:
            if isinstance(obj, h5py.Dataset):
                metadata.update(_describe_dataset(obj))
                meta["shape"] = obj.shape
            else:
                metadata.update(_describe_group(obj))
        except Exception as e:
            meta["warnings"] = [f"H5pyAdapter failed: {e}"]

        if metadata:
            meta["metadata"] = metadata
            meta["nl_summary"] = _build_nl_summary(meta, metadata)
        return meta


def _describe_dataset(dataset: h5py.Dataset) -> dict[str, Any]:
    attrs = {k: safe_repr(v, 100) for k, v in dataset.attrs.items()}
    sample = None
    try:
        if dataset.shape and dataset.shape[0] > 0:
            sample = safe_repr(dataset[0], 100)
    except Exception:
        sample = None

    return {
        "type": "h5py_dataset",
        "name": dataset.name,
        "dtype": str(dataset.dtype),
        "chunks": dataset.chunks,
        "compression": dataset.compression,
        "compression_opts": dataset.compression_opts,
        "attrs": attrs,
        "sample": sample,
    }


def _describe_group(group: h5py.Group) -> dict[str, Any]:
    """Describe dataset structure without reading dataset payloads."""
    datasets: list[dict[str, Any]] = []
    total_datasets = 0
    max_datasets = 100

    def collect(_name: str, item: Any) -> None:
        nonlocal total_datasets
        if not isinstance(item, h5py.Dataset):
            return
        total_datasets += 1
        if len(datasets) >= max_datasets:
            return
        datasets.append(
            {
                "name": item.name,
                "shape": item.shape,
                "dtype": str(item.dtype),
                "chunks": item.chunks,
                "compression": item.compression,
            }
        )

    group.visititems(collect)
    attrs = {key: safe_repr(value, 100) for key, value in group.attrs.items()}
    return {
        "type": "h5py_file" if isinstance(group, h5py.File) else "h5py_group",
        "name": group.name,
        "dataset_count": total_datasets,
        "datasets": datasets,
        "datasets_truncated": total_datasets > max_datasets,
        "attrs": attrs,
    }


if LIBRARY_AVAILABLE:
    AdapterRegistry.register(H5pyAdapter)


def _build_nl_summary(meta: MetaDescription, metadata: dict[str, Any]) -> str:
    if metadata.get("type") in {"h5py_file", "h5py_group"}:
        kind = "file" if metadata["type"] == "h5py_file" else "group"
        datasets = metadata.get("datasets", [])
        count = metadata.get("dataset_count", len(datasets))
        previews = [
            f"{item['name']} (shape {item['shape']}, dtype {item['dtype']})"
            for item in datasets[:8]
        ]
        summary = f"An HDF5 {kind} with {count} dataset{'s' if count != 1 else ''}."
        if previews:
            summary += f" Datasets: {', '.join(previews)}."
        if metadata.get("datasets_truncated"):
            summary += " Dataset listing truncated."
        return summary

    shape = meta.get("shape")
    dtype = metadata.get("dtype")
    name = metadata.get("name")
    chunks = metadata.get("chunks")
    compression = metadata.get("compression")
    compression_opts = metadata.get("compression_opts")
    attrs = metadata.get("attrs")
    sample = metadata.get("sample")
    parts = [f"An HDF5 Dataset '{name}' with shape {shape} and dtype {dtype}."]
    if chunks:
        chunk_desc = f"Chunked: {chunks}."
        if compression:
            level = f" (level {compression_opts})" if compression_opts else ""
            chunk_desc += f" Compression: {compression}{level}."
        parts.append(chunk_desc)
    if attrs:
        parts.append(f"Attributes: {attrs}.")
    if sample is not None:
        parts.append(f"Sample: {sample}.")
    if shape and len(shape) >= 3:
        parts.append(
            f"{shape[0]:,} items, {shape[-2]}x{shape[-1]} elements each."
        )
    return " ".join(parts)
