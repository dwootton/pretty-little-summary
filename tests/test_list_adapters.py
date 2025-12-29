"""Tests for list_available_adapters utility."""

import pretty_little_summary as pls


def test_list_available_adapters_returns_list():
    """Test that list_available_adapters returns a list."""
    adapters = pls.list_available_adapters()
    assert isinstance(adapters, list)


def test_list_available_adapters_contains_strings():
    """Test that all adapter names are strings."""
    adapters = pls.list_available_adapters()
    assert all(isinstance(name, str) for name in adapters)


def test_list_available_adapters_has_generic():
    """Test that GenericAdapter is always present (it's always imported)."""
    adapters = pls.list_available_adapters()
    assert "GenericAdapter" in adapters


def test_list_available_adapters_non_empty():
    """Test that we always have at least one adapter (GenericAdapter)."""
    adapters = pls.list_available_adapters()
    assert len(adapters) > 0


def test_list_available_adapters_unique():
    """Test that adapter names are unique (no duplicates)."""
    adapters = pls.list_available_adapters()
    assert len(adapters) == len(set(adapters))


def test_adapters_available_based_on_imports():
    """Test that adapters are available based on what's installed."""
    adapters = pls.list_available_adapters()

    # These should always be available since they're stdlib or primitives
    expected_always_present = [
        "GenericAdapter",
        "PrimitiveAdapter",
        "CollectionsAdapter",
        "TextFormatAdapter",
    ]

    for adapter in expected_always_present:
        assert adapter in adapters, f"{adapter} should always be present"

    # Try importing pandas - if available, PandasAdapter should be in the list
    try:
        import pandas  # noqa: F401
        assert "PandasAdapter" in adapters
    except ImportError:
        assert "PandasAdapter" not in adapters

    # Try importing matplotlib - if available, MatplotlibAdapter should be in the list
    try:
        import matplotlib  # noqa: F401
        assert "MatplotlibAdapter" in adapters
    except ImportError:
        assert "MatplotlibAdapter" not in adapters


def test_can_call_from_top_level():
    """Test that list_available_adapters is accessible from pretty_little_summary module."""
    assert hasattr(pls, "list_available_adapters")
    assert callable(pls.list_available_adapters)
