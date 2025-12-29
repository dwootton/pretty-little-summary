"""
Test that pretty-little-summary works with minimal dependencies.

This test ensures the library functions correctly when optional
dependencies (pandas, matplotlib, etc.) are not available.
"""

import pretty_little_summary as pls


def test_import_without_optionals():
    """Test that pretty_little_summary can be imported without optional dependencies."""
    assert pls is not None
    assert hasattr(pls, "describe")
    assert hasattr(pls, "Description")
    assert hasattr(pls, "list_available_adapters")


def test_basic_types_without_optionals():
    """Test that basic Python types work without optional dependencies."""
    # Test with various built-in types
    test_cases = [
        42,  # int
        3.14,  # float
        "hello",  # str
        [1, 2, 3],  # list
        {"a": 1, "b": 2},  # dict
        (1, 2, 3),  # tuple
        {1, 2, 3},  # set
        True,  # bool
        None,  # None
    ]

    for obj in test_cases:
        result = pls.describe(obj)
        assert result.content is not None
        assert isinstance(result.content, str)
        assert len(result.content) > 0
        assert result.meta is not None
        assert "object_type" in result.meta
        assert "adapter_used" in result.meta


def test_list_available_adapters_minimal():
    """Test list_available_adapters works with minimal install."""
    adapters = pls.list_available_adapters()

    # These should always be available (stdlib/built-in types)
    required_adapters = [
        "GenericAdapter",
        "PrimitiveAdapter",
        "CollectionsAdapter",
    ]

    for adapter in required_adapters:
        assert adapter in adapters, f"{adapter} should be available in minimal install"


def test_complex_builtin_structures():
    """Test complex but built-in data structures."""
    # Nested structures
    nested_dict = {
        "users": [
            {"name": "Alice", "age": 30, "scores": [95, 88, 92]},
            {"name": "Bob", "age": 25, "scores": [87, 90, 85]},
        ],
        "metadata": {"version": "1.0", "date": "2024-01-01"},
    }

    result = pls.describe(nested_dict)
    assert result.content is not None
    assert "dict" in result.content.lower()

    # List of tuples
    data = [(1, "a"), (2, "b"), (3, "c")]
    result = pls.describe(data)
    assert result.content is not None


def test_generic_adapter_fallback():
    """Test that GenericAdapter works as fallback for unknown types."""

    class CustomClass:
        def __init__(self, value):
            self.value = value
            self.name = "custom"

    obj = CustomClass(42)
    result = pls.describe(obj)

    assert result.content is not None
    assert result.meta is not None
    # Should use GenericAdapter or one of the stdlib adapters
    assert result.meta["adapter_used"] in [
        "GenericAdapter",
        "StructuredAdapter",
        "CallableAdapter",
    ]


def test_callable_objects():
    """Test that functions and callables work."""

    def my_function(x, y):
        return x + y

    result = pls.describe(my_function)
    assert result.content is not None
    assert "my_function" in result.content or "function" in result.content.lower()


def test_metadata_structure():
    """Test that metadata has expected structure."""
    obj = [1, 2, 3, 4, 5]
    result = pls.describe(obj)

    # Check metadata structure
    assert "object_type" in result.meta
    assert "adapter_used" in result.meta

    # For a list, should have additional metadata
    if "metadata" in result.meta:
        meta = result.meta["metadata"]
        assert "type" in meta
        assert meta["type"] == "list"


def test_describe_without_optionals():
    """Test that describe works without optional dependencies."""
    result = pls.describe([1, 2, 3])
    assert result.content is not None
