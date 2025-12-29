"""Base classes for the adapter system."""

from typing import Any, Protocol, Type

from wut_is.core import MetaDescription


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
        from wut_is.adapters.generic import GenericAdapter

        return GenericAdapter


def dispatch_adapter(obj: Any) -> MetaDescription:
    """
    Main dispatcher function - routes object to appropriate adapter.

    Args:
        obj: Any Python object to analyze

    Returns:
        MetaDescription with extracted metadata
    """
    adapter = AdapterRegistry.get_adapter(obj)
    return adapter.extract_metadata(obj)


def list_available_adapters() -> list[str]:
    """
    List all currently registered adapters.

    Returns a list of adapter names that are available based on installed libraries.
    This is useful for debugging and understanding which adapters are active.

    Returns:
        List of adapter class names

    Example:
        >>> import wut_is
        >>> wut_is.list_available_adapters()
        ['PandasAdapter', 'MatplotlibAdapter', 'NumpyAdapter', 'GenericAdapter']
    """
    return [adapter.__name__ for adapter in AdapterRegistry._adapters]
