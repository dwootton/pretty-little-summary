"""Tests for h5py adapter."""

from pathlib import Path

import pytest

import pretty_little_summary as pls
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


def test_h5py_file_lists_datasets_without_reading_payload(tmp_path: Path) -> None:
    path = tmp_path / "measurements.nc"
    with h5py.File(path, "w") as handle:
        handle.create_dataset("temperature", shape=(4, 3), dtype="f4")
        handle.create_dataset("station/id", data=[1, 2, 3])

    result = pls.describe(path, dynamic_imports=True)

    assert result.meta["adapter_used"] == "H5pyAdapter"
    assert result.meta["metadata"]["dataset_count"] == 2
    assert {item["name"] for item in result.meta["metadata"]["datasets"]} == {
        "/station/id",
        "/temperature",
    }
    assert "2 datasets" in result.content
