"""Base classes for the adapter system."""

import sys
from typing import Any, ClassVar, Protocol

from pretty_little_summary.core import MetaDescription


def module_loaded(name: str) -> bool:
    """True if a module is already imported in this process.

    Lets a heavy-library adapter (torch, tensorflow, jax) detect its objects
    without importing the library itself: if the library has not been imported
    by the user's program, it cannot have produced the object being described,
    so there is nothing for the adapter to handle. This is what keeps a bare
    ``describe(df)`` from dragging in multi-second imports.
    """
    return name in sys.modules


class Adapter(Protocol):
    """Protocol for all adapters."""

    @staticmethod
    def can_handle(obj: Any) -> bool:
        """Check if this adapter can handle the object."""
        ...

    @staticmethod
    def extract_metadata(obj: Any) -> MetaDescription:
        """Extract metadata from the object."""
        ...


# Priority tiers. Higher wins; adapters checked highest-first, ties broken by
# registration order (so import order still decides among same-priority peers).
PRIORITY_DEFAULT = 0
PRIORITY_FALLBACK = -1000  # GenericAdapter — always last resort.


class AdapterRegistry:
    """
    Registry for managing adapters.

    Design:
    - Explicit priority ordering (not import order): each adapter registers with
      a priority; higher is checked first, ties broken by registration order.
      This decouples "must be imported last" from "must be checked last".
    - Idempotent registration: re-registering the same class is a no-op, so the
      module can be imported/reloaded without duplicating adapters.
    - Fallback: GenericAdapter for unknown types.
    """

    # Each entry: (priority, sequence, adapter). `sequence` is a stable tiebreaker.
    _entries: ClassVar[list[tuple[int, int, type[Adapter]]]] = []
    _seq: int = 0

    @classmethod
    def register(cls, adapter: type[Adapter], priority: int = PRIORITY_DEFAULT) -> None:
        """Register an adapter at the given priority (idempotent by class)."""
        if any(existing is adapter for _, _, existing in cls._entries):
            return
        cls._entries.append((priority, cls._seq, adapter))
        cls._seq += 1
        # Sort once at registration: highest priority first, then insertion order.
        cls._entries.sort(key=lambda e: (-e[0], e[1]))

    @classmethod
    def get_adapter(cls, obj: Any) -> type[Adapter]:
        """Find the highest-priority adapter that can handle obj."""
        for _, _, adapter in cls._entries:
            try:
                if adapter.can_handle(obj):
                    return adapter
            except Exception:
                # A misbehaving can_handle must never break dispatch.
                continue
        from pretty_little_summary.adapters.generic import GenericAdapter

        return GenericAdapter

    @classmethod
    def unregister(cls, adapter: type[Adapter]) -> None:
        """Remove an adapter if present (no-op otherwise)."""
        cls._entries = [e for e in cls._entries if e[2] is not adapter]

    @classmethod
    def adapters(cls) -> list[type[Adapter]]:
        """Return registered adapter classes in priority order."""
        return [adapter for _, _, adapter in cls._entries]


def dispatch_adapter(obj: Any) -> MetaDescription:
    """
    Main dispatcher function - routes object to appropriate adapter.

    Implements graceful degradation:
    1. Try selected adapter's extract_metadata()
    2. On failure, fall back to GenericAdapter
    3. If GenericAdapter also fails, return minimal MetaDescription

    Args:
        obj: Any Python object to analyze

    Returns:
        MetaDescription with extracted metadata
    """
    _ensure_adapters_loaded()
    adapter = AdapterRegistry.get_adapter(obj)
    adapter_name = adapter.__name__

    try:
        return adapter.extract_metadata(obj)
    except Exception as e:
        # Log the failure for debugging
        warning_msg = f"{adapter_name} failed: {e!s}"

        # If the failed adapter was NOT GenericAdapter, try GenericAdapter
        if adapter_name != "GenericAdapter":
            try:
                from pretty_little_summary.adapters.generic import GenericAdapter

                meta = GenericAdapter.extract_metadata(obj)
                # Add warning about adapter failure
                meta.setdefault("warnings", []).append(warning_msg)
                meta["adapter_used"] = f"{adapter_name} (failed, using GenericAdapter)"
                return meta
            except Exception as fallback_error:
                # Even GenericAdapter failed - return minimal metadata
                return _create_emergency_metadata(obj, adapter_name, e, fallback_error)
        else:
            # GenericAdapter itself failed - return minimal metadata
            return _create_emergency_metadata(obj, adapter_name, e)


def _create_emergency_metadata(
    obj: Any,
    adapter_name: str,
    primary_error: Exception,
    fallback_error: Exception | None = None,
) -> MetaDescription:
    """
    Create minimal metadata when all extraction fails.

    This is the last resort when both the selected adapter and GenericAdapter
    fail to extract metadata. Returns a minimal but valid MetaDescription.

    Args:
        obj: The object that failed extraction
        adapter_name: Name of the adapter that failed
        primary_error: The original error from the adapter
        fallback_error: Optional error from GenericAdapter fallback

    Returns:
        Minimal MetaDescription with error information
    """
    warnings = [f"{adapter_name} failed: {primary_error!s}"]
    if fallback_error:
        warnings.append(f"GenericAdapter fallback also failed: {fallback_error!s}")

    from pretty_little_summary.canonical import canonical_repr

    try:
        raw_repr = canonical_repr(obj, 500)
    except Exception:
        raw_repr = "<repr failed>"

    return {
        "object_type": f"{type(obj).__module__}.{type(obj).__name__}",
        "adapter_used": f"{adapter_name} (emergency fallback)",
        "warnings": warnings,
        "raw_repr": raw_repr,
    }


def _ensure_adapters_loaded() -> None:
    """Import the built-in adapter modules on first use.

    Deferring these imports keeps ``import pretty_little_summary`` instant and,
    for a zero-dependency install, means we never touch a heavy library until
    the user actually asks us to describe something.
    """
    from pretty_little_summary.adapters import load_all_adapters

    load_all_adapters()


def list_available_adapters() -> list[str]:
    """
    List all currently registered adapters, in priority order.

    Returns a list of adapter names that are available based on installed
    libraries. Useful for debugging which adapters are active.

    Example:
        >>> import pretty_little_summary as pls
        >>> pls.list_available_adapters()
        ['PandasAdapter', 'MatplotlibAdapter', 'NumpyAdapter', 'GenericAdapter']
    """
    _ensure_adapters_loaded()
    return [adapter.__name__ for adapter in AdapterRegistry.adapters()]
