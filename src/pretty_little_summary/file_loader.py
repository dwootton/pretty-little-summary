"""Helper functions for loading file contents based on file type."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pretty_little_summary.file_capabilities import detect_file_capability

# Default cap on rows read from row-oriented files (CSV/JSONL/Stata) in deep
# mode. Keeps profiling of huge datasets fast and memory-bounded; pass
# ``sample_rows=None`` (or ``full=True`` at the API layer) to read everything.
DEFAULT_SAMPLE_ROWS = 100_000

# Extensions whose loaders honour ``sample_rows`` (i.e. row-oriented tabular
# formats). Used by :func:`load_file_sampled` to decide whether truncation to
# ``sample_rows`` was even possible.
_ROW_ORIENTED_SUFFIXES = {'.csv', '.jsonl', '.ndjson', '.dta'}


def load_file(
    file_path: Path,
    allow_unpickle: bool = False,
    sample_rows: int | None = None,
) -> Any:
    """
    Load a file and return its content as a Python object.

    This is the *deep*, library-backed loader used only in opt-in deep mode;
    the default description path uses the zero-dependency sniffer tier instead.
    It intelligently loads by extension, falling back to reading as text.

    Args:
        file_path: Path to the file to load
        allow_unpickle: Permit executing pickle files. Off by default because
            unpickling untrusted data runs arbitrary code.
        sample_rows: For row-oriented formats (CSV/JSONL/Stata), read at most
            this many rows. ``None`` (the default) reads the whole file.

    Returns:
        Loaded Python object (DataFrame, dict, Image, etc.) or raw text

    Raises:
        Exception: If file cannot be read
    """
    capability = detect_file_capability(file_path)
    capability_name = capability.name if capability else None

    # CSV files -> pandas DataFrame
    if capability_name == 'csv':
        return _load_csv(file_path, sample_rows)

    # JSON Lines / newline-delimited JSON -> pandas DataFrame
    if capability_name == 'jsonl':
        return _load_jsonl(file_path, sample_rows)

    # JSON files -> dict/list
    if capability_name == 'json':
        return _load_json(file_path)

    # Stata files -> pandas DataFrame
    if capability_name == 'stata':
        return _load_stata(file_path, sample_rows)

    # Parquet files -> pandas DataFrame
    if capability_name == 'parquet':
        return _load_parquet(file_path)

    # Classic NetCDF files -> xarray Dataset via scipy
    if capability_name == 'netcdf':
        return _load_netcdf(file_path)

    # Pickle files -> any Python object (guarded: unpickling executes code)
    if capability_name == 'pickle':
        return _load_pickle(file_path, allow_unpickle)

    # Image files -> PIL Image
    if capability_name == 'image':
        return _load_image(file_path)

    # Text files -> str
    if capability_name == 'text':
        return _load_text(file_path)

    # HDF5 files -> h5py File
    if capability_name == 'hdf5':
        return _load_hdf5(file_path)

    # NumPy files -> ndarray
    if capability_name == 'numpy':
        return _load_numpy(file_path)

    # Default: try to read as text
    return _load_text(file_path)


def load_file_sampled(
    file_path: Path,
    sample_rows: int | None = None,
    full: bool = False,
) -> tuple[Any, bool, int | None]:
    """Load a file for deep profiling, reporting whether it was truncated.

    Wraps :func:`load_file` for the deep-description path. For row-oriented
    tabular formats it reads at most ``sample_rows`` rows (unless ``full``),
    then reports whether that cap actually truncated the data.

    Args:
        file_path: Path to load.
        sample_rows: Row cap for row-oriented formats. Ignored when ``full``.
        full: Read the whole file regardless of size.

    Returns:
        ``(obj, was_sampled, sampled_rows)`` where ``was_sampled`` is True only
        when a row cap actually cut the data short, and ``sampled_rows`` is the
        number of rows kept (``None`` when not row-oriented / not truncated).
    """
    # Resolve the default at call time (not as a default arg) so the module
    # constant can be patched, e.g. in tests.
    if sample_rows is None:
        sample_rows = DEFAULT_SAMPLE_ROWS
    effective_cap = None if full else sample_rows
    obj = load_file(file_path, sample_rows=effective_cap)

    if effective_cap is None:
        return obj, False, None
    if file_path.suffix.lower() not in _ROW_ORIENTED_SUFFIXES:
        return obj, False, None

    # A DataFrame filled exactly to the cap almost certainly had more rows.
    n_rows = getattr(obj, "shape", (None,))[0]
    if isinstance(n_rows, int) and n_rows >= effective_cap:
        return obj, True, n_rows
    return obj, False, None


def _load_csv(file_path: Path, sample_rows: int | None = None) -> Any:
    """Load CSV file as pandas DataFrame."""
    try:
        import pandas as pd
        return pd.read_csv(file_path, nrows=sample_rows)
    except ImportError:
        # Fallback: read as text
        return _load_text(file_path)


def _load_jsonl(file_path: Path, sample_rows: int | None = None) -> Any:
    """Load JSON Lines / newline-delimited JSON as a pandas DataFrame."""
    try:
        import pandas as pd
        return pd.read_json(file_path, lines=True, nrows=sample_rows)
    except ImportError:
        # Fallback: read as text
        return _load_text(file_path)


def _load_stata(file_path: Path, sample_rows: int | None = None) -> Any:
    """Load a Stata ``.dta`` file as a pandas DataFrame.

    When ``sample_rows`` is set, read only the first chunk via Stata's native
    iterator instead of materialising the whole file.
    """
    try:
        import pandas as pd
    except ImportError:
        raise ImportError("pandas required to load Stata (.dta) files")
    if sample_rows is None:
        return pd.read_stata(file_path)
    import warnings
    with warnings.catch_warnings():
        # Chunked reads can't know all category labels up front; harmless for a
        # profiling sample, so silence the expected CategoricalConversionWarning.
        warnings.simplefilter("ignore")
        with pd.read_stata(file_path, chunksize=sample_rows) as reader:
            for chunk in reader:
                return chunk
    # File had zero rows: return an empty frame with the right columns.
    return pd.read_stata(file_path)


def _load_json(file_path: Path) -> Any:
    """Load JSON file as dict/list."""
    with open(file_path) as f:
        return json.load(f)


def _load_parquet(file_path: Path) -> Any:
    """Load Parquet file as pandas DataFrame."""
    try:
        import pandas as pd
        return pd.read_parquet(file_path)
    except ImportError:
        raise ImportError("pandas with pyarrow/fastparquet required to load Parquet files")


def _load_netcdf(file_path: Path) -> Any:
    """Load classic NetCDF as an xarray Dataset using scipy's backend."""
    try:
        import xarray as xr

        return xr.open_dataset(file_path, engine="scipy")
    except ImportError:
        raise ImportError("xarray and scipy required to load classic NetCDF files") from None


def _load_pickle(file_path: Path, allow_unpickle: bool = False) -> Any:
    """Load a pickle file as a Python object.

    Refuses by default: ``pickle.load`` executes arbitrary code embedded in the
    file, so it must never run implicitly on files pls is merely describing. The
    sniffer tier inspects pickles safely (protocol + referenced globals) without
    executing them.
    """
    if not allow_unpickle:
        raise PermissionError(
            "Refusing to unpickle by default (arbitrary code execution risk). "
            "Pass allow_unpickle=True to override."
        )
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
        with open(file_path, encoding='utf-8') as f:
            content = f.read(max_size)
            # Check if there's more content
            if f.read(1):
                content += f"\n... (file truncated at {max_size} characters)"
            return content
    except UnicodeDecodeError:
        # Try with latin-1 encoding as fallback
        with open(file_path, encoding='latin-1') as f:
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
        if file_path.suffix.lower() == '.npy':
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
