"""Deterministic, version-stable value formatting.

`pls` promises byte-identical output for the same input across runs, platforms,
and — the hard one — library versions. The main threat to that promise is
``repr()`` of third-party scalars: numpy 2.x changed its scalar repr from ``1``
to ``np.int64(1)``, so any summary that embedded ``repr(np.int64(1))`` silently
changed output on a library upgrade.

Everything that turns a value into text for a summary should go through here so
the formatting rules live in exactly one place. This module imports no
third-party libraries; it detects them by duck typing / module name so it works
in a zero-dependency install.
"""

from __future__ import annotations

import math
import re
from typing import Any

__all__ = [
    "canonical_repr",
    "canonical_str",
    "format_float",
    "strip_memory_addresses",
    "to_python_scalar",
]

# Default object reprs embed the instance's id, e.g.
# ``<pkg.Klass object at 0x10f3c2a90>``. That address varies every run, so any
# summary that captured it would not be deterministic. Normalise it away.
_MEM_ADDRESS_RE = re.compile(r" at 0x[0-9A-Fa-f]+")


def strip_memory_addresses(text: str) -> str:
    """Remove ``at 0x…`` instance addresses so reprs are run-stable."""
    return _MEM_ADDRESS_RE.sub("", text)

# Precision used when a float has no exact short decimal form. Python's float
# repr is already shortest-round-trip and platform-stable, so we only clamp
# pathological values; this constant documents intent for future changes.
_FLOAT_PRECISION = 12


def to_python_scalar(obj: Any) -> Any:
    """Unwrap a library scalar (numpy, etc.) into a plain Python value.

    Leaves ordinary Python objects untouched. This is what makes ``repr`` of a
    sampled value stable: ``np.int64(1)`` becomes ``1`` regardless of the numpy
    version doing the wrapping.
    """
    module = type(obj).__module__ or ""

    # numpy scalars (np.int64, np.float32, np.bool_) and 0-d arrays expose
    # .item(); numpy is the overwhelmingly common case but any array-api scalar
    # that follows the convention works too.
    if module.startswith(("numpy", "jax", "torch", "tensorflow")):
        item = getattr(obj, "item", None)
        # Only 0-d / scalar-like objects have a meaningful .item(); guard on
        # ndim so we don't collapse a whole array to a single element.
        ndim = getattr(obj, "ndim", 0)
        if callable(item) and (ndim == 0 or ndim is None):
            try:
                return item()
            except Exception:
                return obj

    return obj


def format_float(value: float) -> str:
    """Format a float deterministically.

    Python's ``repr(float)`` is shortest-round-trip and stable across platforms
    since 3.1, so we lean on it and only special-case non-finite values (whose
    repr — ``inf``/``nan`` — is fine, but we spell them consistently).
    """
    if math.isnan(value):
        return "nan"
    if math.isinf(value):
        return "inf" if value > 0 else "-inf"
    return repr(value)


def canonical_repr(obj: Any, max_len: int = 50) -> str:
    """Deterministic ``repr``-style string with a length cap.

    Drop-in replacement for ad-hoc ``repr(obj)[:n]`` calls: unwraps library
    scalars first so the result does not depend on a third-party version.
    """
    try:
        value = to_python_scalar(obj)
        if isinstance(value, float):
            r = format_float(value)
        else:
            r = strip_memory_addresses(repr(value))
    except Exception:
        return f"<{type(obj).__name__}>"

    if len(r) > max_len:
        return r[: max(0, max_len - 3)] + "..."
    return r


def canonical_str(obj: Any, max_len: int = 100) -> str:
    """Deterministic ``str``-style string with a length cap."""
    try:
        value = to_python_scalar(obj)
        if isinstance(value, float):
            s = format_float(value)
        else:
            s = strip_memory_addresses(str(value))
    except Exception:
        return f"<{type(obj).__name__}>"

    if len(s) > max_len:
        return s[: max(0, max_len - 3)] + "..."
    return s
