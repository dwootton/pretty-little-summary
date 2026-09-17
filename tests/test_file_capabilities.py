"""Tests for general file capability and dynamic import discovery."""

from __future__ import annotations

import importlib
import sys
from pathlib import Path
from types import SimpleNamespace

import pretty_little_summary as pls
from pretty_little_summary.file_capabilities import (
    detect_file_capability,
    import_available_requirements,
    requirements_for_path,
)
from pretty_little_summary.file_loader import load_file


def test_requirements_cover_general_file_families(tmp_path: Path) -> None:
    cases = {
        "data.csv": [("pandas", "pandas")],
        "data.parquet": [("pandas", "pandas"), ("pyarrow", "pyarrow")],
        "image.png": [("PIL", "pillow")],
        "array.npy": [("numpy", "numpy")],
        "notes.txt": [],
    }
    for filename, expected in cases.items():
        path = tmp_path / filename
        path.write_bytes(b"not a real payload")
        actual = [
            (requirement.import_name, requirement.package_name)
            for requirement in requirements_for_path(path)
        ]
        assert actual == expected


def test_magic_bytes_override_domain_specific_suffix(tmp_path: Path) -> None:
    path = tmp_path / "climate.nc"
    path.write_bytes(b"\x89HDF\r\n\x1a\n" + b"payload")

    capability = detect_file_capability(path)
    assert capability is not None
    assert capability.name == "hdf5"
    assert requirements_for_path(path)[0].import_name == "h5py"


def test_classic_netcdf_resolves_xarray_and_scipy(tmp_path: Path) -> None:
    path = tmp_path / "climate.nc"
    path.write_bytes(b"CDF\x02" + b"payload")

    assert [item.import_name for item in requirements_for_path(path)] == [
        "xarray",
        "scipy",
    ]


def test_hdf5_user_block_signature_is_detected(tmp_path: Path) -> None:
    path = tmp_path / "domain-data.nc"
    path.write_bytes(b"\0" * 512 + b"\x89HDF\r\n\x1a\n" + b"payload")

    capability = detect_file_capability(path)
    assert capability is not None
    assert capability.name == "hdf5"


def test_classic_netcdf_uses_registered_loader(tmp_path: Path, monkeypatch) -> None:
    path = tmp_path / "climate.nc"
    path.write_bytes(b"CDF\x01" + b"payload")
    sentinel = object()
    calls: list[tuple[Path, str]] = []

    def open_dataset(value: Path, *, engine: str):
        calls.append((value, engine))
        return sentinel

    monkeypatch.setitem(sys.modules, "xarray", SimpleNamespace(open_dataset=open_dataset))

    assert load_file(path) is sentinel
    assert calls == [(path, "scipy")]


def test_directory_requirements_are_ordered_and_deduplicated(tmp_path: Path) -> None:
    (tmp_path / "a.csv").write_text("a\n1\n")
    (tmp_path / "b.csv").write_text("b\n2\n")
    (tmp_path / "c.npy").write_bytes(b"not numpy")

    assert [item.import_name for item in requirements_for_path(tmp_path)] == [
        "pandas",
        "numpy",
    ]


def test_native_dynamic_imports_never_use_micropip(
    tmp_path: Path,
    monkeypatch,
) -> None:
    path = tmp_path / "data.csv"
    path.write_text("a\n1\n")
    requested: list[str] = []

    def fake_import(name: str):
        requested.append(name)
        raise ModuleNotFoundError(name)

    monkeypatch.setattr(importlib, "import_module", fake_import)
    missing = import_available_requirements(path)

    assert requested == ["pandas"]
    assert [item.import_name for item in missing] == ["pandas"]
    assert "micropip" not in requested


def test_describe_accepts_dynamic_imports_in_native_python(
    tmp_path: Path,
    monkeypatch,
) -> None:
    path = tmp_path / "notes.txt"
    path.write_text("hello")
    calls: list[Path] = []

    monkeypatch.setattr(
        "pretty_little_summary.file_capabilities.import_available_requirements",
        lambda value: calls.append(Path(value)) or (),
    )

    result = pls.describe(path, dynamic_imports=True)
    assert calls == [path]
    assert result.content
