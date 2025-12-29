"""Tests for h5py adapter."""

import pytest

from wut_is.adapters import dispatch_adapter
from wut_is.synthesizer import deterministic_summary


h5py = pytest.importorskip("h5py")


def test_h5py_dataset() -> None:
    with h5py.File("in_memory.h5", "w", driver="core", backing_store=False) as f:
        dset = f.create_dataset("data", data=[1, 2, 3])
        meta = dispatch_adapter(dset)
        assert meta["adapter_used"] == "H5pyAdapter"
        assert meta["metadata"]["type"] == "h5py_dataset"
        print("h5py:", deterministic_summary(meta))
        assert "HDF5 Dataset" in deterministic_summary(meta)
