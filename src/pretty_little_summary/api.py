"""Main API entry point for pretty_little_summary."""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from pretty_little_summary.adapters import dispatch_adapter
from pretty_little_summary.core import HistorySlicer
from pretty_little_summary.synthesizer import deterministic_summary


@dataclass
class Description:
    """
    Result object from pls.describe().

    Attributes:
        content: Structured summary of what the object is
        meta: Structured metadata (Schema, Stats, Adapter Used)
        history: Code history if available from IPython/Jupyter
    """

    content: str
    meta: dict
    history: list[str] | None


def describe(
    obj: Any,
    name: str | None = None,
    *,
    shallow: bool = False,
    full: bool = False,
) -> Description:
    """
    Generate a structured summary of any Python object.

    This is the main entry point for pretty_little_summary. It:
    1. Extracts metadata using type-specific adapters
    2. Retrieves code history (if in IPython/Jupyter)
    3. Generates a deterministic summary

    Filesystem paths are first-class. Pass a ``pathlib.Path`` (or a plain string
    that names an existing file/directory — it is promoted to ``Path``
    automatically) to describe what is on disk. By default a path is loaded
    into a rich object (e.g. a DataFrame) and given a full profile — row
    counts, nulls, and per-column stats — with every dataset in a directory
    deep-profiled too. Pass ``shallow=True`` to skip loading and describe only
    from a cheap head sample (zero dependencies, never executes or fully loads
    file content).

    Args:
        obj: Any Python object to analyze. A string naming an existing path is
            promoted to ``pathlib.Path``.
        name: Optional variable name for history filtering.
              If None, attempts to auto-detect from calling context.
        shallow: For paths, describe only from a head sample instead of
            loading and fully profiling the file(s). No effect on non-path
            objects.
        full: For a deep row-oriented file load, read every row instead of a
            bounded sample. No effect when ``shallow`` is set.

    Returns:
        Description object with content, meta, and history attributes

    Examples:
        >>> import pretty_little_summary as pls
        >>> import pandas as pd
        >>> df = pd.read_csv("data.csv")
        >>> result = pls.describe(df)
        >>> print(result.content)
        "pandas.DataFrame | Shape: (1000, 5) | Columns: product, price, quantity, date, customer_id"
        >>> print(result.meta)
        {'object_type': 'pandas.DataFrame', 'shape': (1000, 5), ...}

        >>> # Describe a file straight from disk — full profile by default:
        >>> print(pls.describe("data.csv").content)                  # full profile
        >>> print(pls.describe("data.csv", shallow=True).content)    # head sniff + tip
    """
    # Promote a string that names an existing path to a Path so callers can pass
    # "data.csv" instead of Path("data.csv"). Existence-gated so ordinary
    # strings are described as strings, unchanged.
    if isinstance(obj, str) and _looks_like_existing_path(obj):
        obj = Path(obj)

    is_path = isinstance(obj, Path)

    # Auto-detect variable name if not provided
    if name is None:
        name = _try_get_variable_name(obj)

    # Extract metadata. Paths flow through describe_path so deep loading and
    # directory profiling share one entry point; everything else uses adapters.
    if is_path:
        from pretty_little_summary.sniffers._base import describe_path

        metadata = describe_path(obj, deep=not shallow, full=full)
    else:
        metadata = dispatch_adapter(obj)

    # Get history if available
    history: list[str] | None = None
    if HistorySlicer.is_ipython_environment():
        history = HistorySlicer.get_history(var_name=name, max_lines=50)

    # Generate deterministic summary
    content = deterministic_summary(metadata, history)

    # Nudge back toward the full profile when a path was described shallowly.
    if is_path and shallow:
        content += (
            "\nTip: drop shallow=True to load and fully profile this "
            f"{'directory' if obj.is_dir() else 'file'}."
        )

    # Return Description object
    return Description(content=content, meta=metadata, history=history)


def _looks_like_existing_path(value: str) -> bool:
    """True when a string names an existing file/dir and is safe to promote.

    Guards against pathological inputs (very long strings, embedded newlines)
    that are clearly data rather than paths, then checks the filesystem.
    """
    if not value or len(value) > 4096 or "\n" in value or "\x00" in value:
        return False
    try:
        return os.path.exists(value)
    except (OSError, ValueError):
        return False


def _try_get_variable_name(obj: Any) -> str | None:
    """
    Attempt to auto-detect variable name from IPython namespace.

    Strategy:
    - Access get_ipython().user_ns (namespace dict)
    - Find variable(s) that reference the same object (using `is`)
    - Return the first match (or None)

    This is best-effort; may not work for complex cases.

    Args:
        obj: Object to find variable name for

    Returns:
        Variable name if found, None otherwise
    """
    try:
        from IPython import get_ipython

        ip = get_ipython()
        if ip is None:
            return None

        # Search namespace for matching object
        for var_name, var_obj in ip.user_ns.items():
            if var_obj is obj and not var_name.startswith("_"):
                return var_name

    except (ImportError, AttributeError):
        pass

    return None
