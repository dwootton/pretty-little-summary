"""Helper functions for loading file contents based on file type."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_file(file_path: Path) -> Any:
    """
    Load a file and return its content as a Python object.

    Attempts to intelligently load the file based on its extension,
    falling back to reading as text if no specific loader is available.

    Args:
        file_path: Path to the file to load

    Returns:
        Loaded Python object (DataFrame, dict, Image, etc.) or raw text

    Raises:
        Exception: If file cannot be read
    """
    suffix = file_path.suffix.lower()

    # CSV files -> pandas DataFrame
    if suffix == '.csv':
        return _load_csv(file_path)

    # JSON files -> dict/list
    if suffix == '.json':
        return _load_json(file_path)

    # Parquet files -> pandas DataFrame
    if suffix in {'.parquet', '.pq'}:
        return _load_parquet(file_path)

    # Pickle files -> any Python object
    if suffix in {'.pkl', '.pickle'}:
        return _load_pickle(file_path)

    # Image files -> PIL Image
    if suffix in {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp'}:
        return _load_image(file_path)

    # Text files -> str
    if suffix in {'.txt', '.md', '.rst', '.log', '.py', '.js', '.html', '.css', '.yaml', '.yml', '.toml', '.ini', '.cfg'}:
        return _load_text(file_path)

    # HDF5 files -> h5py File
    if suffix in {'.h5', '.hdf5'}:
        return _load_hdf5(file_path)

    # NumPy files -> ndarray
    if suffix in {'.npy', '.npz'}:
        return _load_numpy(file_path)

    # Default: try to read as text
    return _load_text(file_path)


def _load_csv(file_path: Path) -> Any:
    """Load CSV file as pandas DataFrame."""
    try:
        import pandas as pd
        return pd.read_csv(file_path)
    except ImportError:
        # Fallback: read as text
        return _load_text(file_path)


def _load_json(file_path: Path) -> Any:
    """Load JSON file as dict/list."""
    with open(file_path, 'r') as f:
        return json.load(f)


def _load_parquet(file_path: Path) -> Any:
    """Load Parquet file as pandas DataFrame."""
    try:
        import pandas as pd
        return pd.read_parquet(file_path)
    except ImportError:
        raise ImportError("pandas with pyarrow/fastparquet required to load Parquet files")


def _load_pickle(file_path: Path) -> Any:
    """Load pickle file as Python object."""
    import pickle
    with open(file_path, 'rb') as f:
        return pickle.load(f)


def _load_image(file_path: Path) -> Any:
    """Load image file as PIL Image."""
    try:
        from PIL import Image
        return Image.open(file_path)
    except ImportError:
        raise ImportError("pillow required to load image files")


def _load_text(file_path: Path, max_size: int = 10_000) -> str:
    """
    Load text file as string.

    Args:
        file_path: Path to text file
        max_size: Maximum number of characters to read (default 10,000)

    Returns:
        File contents as string (truncated if too large)
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read(max_size)
            # Check if there's more content
            if f.read(1):
                content += f"\n... (file truncated at {max_size} characters)"
            return content
    except UnicodeDecodeError:
        # Try with latin-1 encoding as fallback
        with open(file_path, 'r', encoding='latin-1') as f:
            content = f.read(max_size)
            if f.read(1):
                content += f"\n... (file truncated at {max_size} characters)"
            return content


def _load_hdf5(file_path: Path) -> Any:
    """Load HDF5 file."""
    try:
        import h5py
        return h5py.File(file_path, 'r')
    except ImportError:
        raise ImportError("h5py required to load HDF5 files")


def _load_numpy(file_path: Path) -> Any:
    """Load NumPy array file."""
    try:
        import numpy as np
        if file_path.suffix == '.npy':
            return np.load(file_path)
        else:  # .npz
            return np.load(file_path)
    except ImportError:
        raise ImportError("numpy required to load NumPy files")


def should_describe_file(file_path: Path, max_file_size: int = 100_000_000) -> bool:
    """
    Determine if a file should be described based on size and type.

    Args:
        file_path: Path to file
        max_file_size: Maximum file size in bytes (default 100MB)

    Returns:
        True if file should be described, False otherwise
    """
    try:
        # Check file size
        size = file_path.stat().st_size
        if size > max_file_size:
            return False

        # Skip binary files that we can't handle
        suffix = file_path.suffix.lower()
        skip_extensions = {
            '.exe', '.dll', '.so', '.dylib', '.bin',
            '.zip', '.tar', '.gz', '.bz2', '.7z',
            '.pdf', '.doc', '.docx', '.xls', '.xlsx',
            '.mp3', '.mp4', '.avi', '.mov', '.wav',
        }

        return suffix not in skip_extensions

    except Exception:
        return False
