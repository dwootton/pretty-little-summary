"""File format detection and optional import requirements.

This module is intentionally dependency-free.  It is the shared capability
registry used by the native loader and by environments (such as Pyodide) that
need to install optional packages before calling :func:`describe`.
"""

from __future__ import annotations

import importlib
import os
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ImportRequirement:
    """An import name and the package that provides it."""

    import_name: str
    package_name: str


@dataclass(frozen=True)
class FileCapability:
    """A loader capability selected by magic bytes or file suffix."""

    name: str
    suffixes: tuple[str, ...]
    imports: tuple[ImportRequirement, ...] = ()
    signatures: tuple[bytes, ...] = ()


PANDAS = ImportRequirement("pandas", "pandas")
PYARROW = ImportRequirement("pyarrow", "pyarrow")
PILLOW = ImportRequirement("PIL", "pillow")
NUMPY = ImportRequirement("numpy", "numpy")
H5PY = ImportRequirement("h5py", "h5py")
XARRAY = ImportRequirement("xarray", "xarray")
SCIPY = ImportRequirement("scipy", "scipy")


# Magic-aware capabilities come first.  This lets an HDF5-backed file with a
# domain-specific suffix (for example .nc) select the HDF5 loader without a
# one-off special case.  Adding a format is one registry entry rather than a
# new browser tier.
FILE_CAPABILITIES: tuple[FileCapability, ...] = (
    FileCapability(
        "hdf5",
        (".h5", ".hdf5"),
        (H5PY,),
        (b"\x89HDF\r\n\x1a\n",),
    ),
    FileCapability("parquet", (".parquet", ".pq"), (PANDAS, PYARROW), (b"PAR1",)),
    FileCapability(
        "netcdf",
        (".nc",),
        (XARRAY, SCIPY),
        (b"CDF\x01", b"CDF\x02", b"CDF\x05"),
    ),
    FileCapability("csv", (".csv",), (PANDAS,)),
    FileCapability("jsonl", (".jsonl", ".ndjson"), (PANDAS,)),
    FileCapability("stata", (".dta",), (PANDAS,)),
    FileCapability(
        "image",
        (".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tiff", ".webp"),
        (PILLOW,),
    ),
    FileCapability("numpy", (".npy", ".npz"), (NUMPY,)),
    FileCapability("json", (".json",)),
    FileCapability("pickle", (".pkl", ".pickle")),
    FileCapability(
        "text",
        (
            ".txt", ".md", ".rst", ".log", ".py", ".js", ".html",
            ".css", ".yaml", ".yml", ".toml", ".ini", ".cfg",
        ),
    ),
)

MAX_REQUIREMENT_SCAN_FILES = 512


def detect_file_capability(path: Path, head: bytes | None = None) -> FileCapability | None:
    """Return the registered capability for *path*, preferring file signatures."""
    if head is None:
        try:
            with path.open("rb") as file:
                head = file.read(65_536)
        except OSError:
            head = b""

    for capability in FILE_CAPABILITIES:
        if _matches_signature(capability, head):
            return capability

    suffix = path.suffix.lower()
    for capability in FILE_CAPABILITIES:
        if suffix in capability.suffixes:
            return capability
    return None


def _matches_signature(capability: FileCapability, head: bytes) -> bool:
    if any(head.startswith(signature) for signature in capability.signatures):
        return True
    if capability.name != "hdf5" or not capability.signatures:
        return False

    # HDF5 permits a user block before the superblock. The signature is then at
    # offset 512 or a later power of two; keep the probe bounded to the head.
    signature = capability.signatures[0]
    offset = 512
    while offset + len(signature) <= len(head):
        if head[offset : offset + len(signature)] == signature:
            return True
        offset *= 2
    return False


def requirements_for_path(path: str | Path) -> tuple[ImportRequirement, ...]:
    """Return optional imports needed for a rich description of a file or tree."""
    resolved = Path(path)
    if resolved.is_dir():
        requirements: list[ImportRequirement] = []
        seen: set[str] = set()
        for child in _iter_directory_files(resolved):
            for requirement in requirements_for_path(child):
                if requirement.import_name not in seen:
                    requirements.append(requirement)
                    seen.add(requirement.import_name)
        return tuple(requirements)

    capability = detect_file_capability(resolved)
    return capability.imports if capability else ()


def _iter_directory_files(root: Path) -> Iterator[Path]:
    """Yield a deterministic, bounded set of files without following symlinks."""
    yielded = 0
    for directory, dirnames, filenames in os.walk(root, followlinks=False):
        dirnames.sort()
        for filename in sorted(filenames):
            yield Path(directory) / filename
            yielded += 1
            if yielded >= MAX_REQUIREMENT_SCAN_FILES:
                return


def import_available_requirements(path: str | Path) -> tuple[ImportRequirement, ...]:
    """Import installed requirements and return those that are unavailable.

    This never installs packages.  Native Python environments stay free of
    network and package-manager side effects; async hosts can install the
    returned requirements using their own mechanism and retry.
    """
    missing: list[ImportRequirement] = []
    for requirement in requirements_for_path(path):
        try:
            importlib.import_module(requirement.import_name)
        except ImportError:
            missing.append(requirement)
    return tuple(missing)
