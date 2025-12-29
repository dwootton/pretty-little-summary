"""Tests for h5py adapter."""

import pytest

from pretty_little_summary.adapters import dispatch_adapter
from pretty_little_summary.synthesizer import deterministic_summary


h5py = pytest.importorskip("h5py")


def test_h5py_dataset() -> None:
    with h5py.File("in_memory.h5", "w", driver="core", backing_store=False) as f:
        dset = f.create_dataset("data", data=[1, 2, 3])
        meta = dispatch_adapter(dset)
        assert meta["adapter_used"] == "H5pyAdapter"
        assert meta["metadata"]["type"] == "h5py_dataset"
        summary = deterministic_summary(meta)
        print("h5py:", summary)
        assert summary == "An HDF5 Dataset '/data' with shape (3,) and dtype int64. Sample: 1."
