"""Base classes for the adapter system."""

from typing import Any, Protocol, Type

from pretty_little_summary.core import MetaDescription


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


class AdapterRegistry:
    """
    Registry for managing adapters.

    Design:
    - Lazy loading: Only import libraries when needed
    - Priority ordering: Check adapters in registration order
    - Fallback: GenericAdapter for unknown types
    """

    _adapters: list[Type[Adapter]] = []

    @classmethod
    def register(cls, adapter: Type[Adapter]) -> None:
        """Register a new adapter."""
        cls._adapters.append(adapter)

    @classmethod
    def get_adapter(cls, obj: Any) -> Type[Adapter]:
        """Find the first adapter that can handle obj."""
        for adapter in cls._adapters:
            if adapter.can_handle(obj):
                return adapter
        # Import GenericAdapter on-demand to avoid circular import
        from pretty_little_summary.adapters.generic import GenericAdapter

        return GenericAdapter


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
    adapter = AdapterRegistry.get_adapter(obj)
    adapter_name = adapter.__name__

    try:
        return adapter.extract_metadata(obj)
    except Exception as e:
        # Log the failure for debugging
        warning_msg = f"{adapter_name} failed: {str(e)}"

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
    warnings = [f"{adapter_name} failed: {str(primary_error)}"]
    if fallback_error:
        warnings.append(f"GenericAdapter fallback also failed: {str(fallback_error)}")

    try:
        raw_repr = repr(obj)[:500]
    except Exception:
        raw_repr = "<repr failed>"

    return {
        "object_type": f"{type(obj).__module__}.{type(obj).__name__}",
        "adapter_used": f"{adapter_name} (emergency fallback)",
        "warnings": warnings,
        "raw_repr": raw_repr,
    }


def list_available_adapters() -> list[str]:
    """
    List all currently registered adapters.

    Returns a list of adapter names that are available based on installed libraries.
    This is useful for debugging and understanding which adapters are active.

    Returns:
        List of adapter class names

    Example:
        >>> import pretty_little_summary as pls
        >>> pls.list_available_adapters()
        ['PandasAdapter', 'MatplotlibAdapter', 'NumpyAdapter', 'GenericAdapter']
    """
    return [adapter.__name__ for adapter in AdapterRegistry._adapters]
