"""Tests for h5py adapter."""

import pytest

from pretty_little_summary.adapters import dispatch_adapter
from pretty_little_summary.synthesizer import deterministic_summary
from tests.input import expected_output, load_example


h5py = pytest.importorskip("h5py")


def test_h5py_dataset() -> None:
    example = load_example("h5py_dataset")
    dset, handle = example.build()
    try:
        meta = dispatch_adapter(dset)
        assert meta["adapter_used"] == "H5pyAdapter"
        assert meta["metadata"]["type"] == "h5py_dataset"
        summary = deterministic_summary(meta)
        print("h5py:", summary)
        assert summary == expected_output(example, meta)
    finally:
        handle.close()
