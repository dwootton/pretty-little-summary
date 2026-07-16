"""Adapter system for pretty_little_summary.

Adapter modules are imported lazily via :func:`load_all_adapters`, which runs on
the first ``describe()`` / ``list_available_adapters()`` call rather than at
``import pretty_little_summary`` time. This keeps import instant and avoids
pulling in heavy optional libraries until they are actually needed.
"""

from pretty_little_summary.adapters._base import (
    Adapter,
    AdapterRegistry,
    dispatch_adapter,
    list_available_adapters,
)

# Registration order among same-priority adapters still matters (it is the
# tiebreaker), so this list is the source of truth for that order. Specialized
# adapters come first; GenericAdapter registers itself at fallback priority.
_ADAPTER_MODULES: tuple[str, ...] = (
    "text_formats",
    "primitives",
    "pandas",
    "polars",
    "matplotlib",
    "altair",
    "seaborn_adapter",
    "plotly_adapter",
    "bokeh_adapter",
    "sklearn_pipeline",
    "sklearn",
    "statsmodels_adapter",
    "numpy_adapter",
    "scipy_sparse_adapter",
    "pyarrow_adapter",
    "h5py_adapter",
    "pil_adapter",
    "pytorch",
    "tensorflow_adapter",
    "jax_adapter",
    "xarray",
    "pydantic",
    "networkx",
    "requests",
    "datetime_adapter",
    "pathlib_adapter",
    "regex_adapter",
    "uuid_adapter",
    "io_adapter",
    "attrs_adapter",
    "ipython_display",
    "structured",
    "callables",
    "async_adapter",
    "errors",
    # Core collections come after specialized adapters so they don't shadow them.
    "collections",
    # GenericAdapter (fallback) is imported last and self-registers lowest.
    "generic",
)

_loaded = False


def load_all_adapters() -> None:
    """Import every built-in adapter module once (idempotent).

    Each module self-registers with :class:`AdapterRegistry` on import. Modules
    whose backing library is unavailable raise ``ImportError`` and are skipped;
    :meth:`AdapterRegistry.register` is idempotent, so calling this repeatedly is
    safe.
    """
    global _loaded
    if _loaded:
        return

    from importlib import import_module

    for name in _ADAPTER_MODULES:
        try:
            import_module(f"pretty_little_summary.adapters.{name}")
        except ImportError:
            # Optional dependency for this adapter is not installed — skip it.
            continue

    _loaded = True


__all__ = [
    "Adapter",
    "AdapterRegistry",
    "dispatch_adapter",
    "list_available_adapters",
    "load_all_adapters",
]
