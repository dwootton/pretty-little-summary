"""Tests for dispatch-level error handling and adapter fallback behavior."""

from typing import Any
from unittest.mock import patch

import pretty_little_summary as pls
from pretty_little_summary.adapters._base import AdapterRegistry, dispatch_adapter
from pretty_little_summary.adapters.generic import GenericAdapter
from pretty_little_summary.core import MetaDescription


class CustomTestObject:
    """Test object for adapter failure scenarios."""

    def __init__(self, value: str = "test"):
        self.value = value

    def __repr__(self):
        return f"CustomTestObject(value={self.value!r})"


class BrokenAdapter:
    """Adapter that always fails during metadata extraction."""

    @staticmethod
    def can_handle(obj: Any) -> bool:
        return isinstance(obj, CustomTestObject)

    @staticmethod
    def extract_metadata(obj: Any) -> MetaDescription:
        raise RuntimeError("Intentional adapter failure for testing")


class PartiallyBrokenAdapter:
    """Adapter that fails with a specific error type."""

    @staticmethod
    def can_handle(obj: Any) -> bool:
        return isinstance(obj, CustomTestObject)

    @staticmethod
    def extract_metadata(obj: Any) -> MetaDescription:
        raise AttributeError("Method 'new_method' not found - version incompatibility")


def test_dispatch_adapter_fallback_to_generic():
    """When an adapter fails, should fall back to GenericAdapter."""
    # Register a broken adapter at the BEGINNING (before GenericAdapter)
    AdapterRegistry._adapters.insert(0, BrokenAdapter)

    try:
        obj = CustomTestObject("fallback_test")
        meta = dispatch_adapter(obj)

        # Should get GenericAdapter result with fallback notation
        assert "adapter_used" in meta
        assert "GenericAdapter" in meta["adapter_used"]
        assert "BrokenAdapter" in meta["adapter_used"]  # Should mention original adapter
        assert "failed" in meta["adapter_used"]

        # Should have warning about failure
        assert "warnings" in meta
        assert any("BrokenAdapter failed" in w for w in meta["warnings"])
        assert any("Intentional adapter failure" in w for w in meta["warnings"])

        # Should still have basic metadata
        assert "object_type" in meta
        assert "CustomTestObject" in meta["object_type"]

    finally:
        # Clean up: remove BrokenAdapter from registry
        AdapterRegistry._adapters = [
            a for a in AdapterRegistry._adapters if a != BrokenAdapter
        ]


def test_dispatch_adapter_attribute_error_fallback():
    """Test fallback when adapter fails with AttributeError (version incompatibility)."""
    # Register adapter that simulates version incompatibility at the BEGINNING
    AdapterRegistry._adapters.insert(0, PartiallyBrokenAdapter)

    try:
        obj = CustomTestObject("version_test")
        meta = dispatch_adapter(obj)

        # Should fall back to GenericAdapter
        assert "GenericAdapter" in meta["adapter_used"]
        assert "PartiallyBrokenAdapter" in meta["adapter_used"]
        assert "failed" in meta["adapter_used"]

        # Should have warning about the specific error
        assert "warnings" in meta
        assert any("new_method" in w for w in meta["warnings"])
        assert any("version incompatibility" in w for w in meta["warnings"])

    finally:
        AdapterRegistry._adapters = [
            a for a in AdapterRegistry._adapters if a != PartiallyBrokenAdapter
        ]


def test_dispatch_emergency_fallback():
    """When GenericAdapter itself fails, return emergency metadata."""
    # Save original extract_metadata
    original_extract = GenericAdapter.extract_metadata

    # Mock GenericAdapter to fail
    def failing_extract(obj):
        raise RuntimeError("GenericAdapter also failed!")

    GenericAdapter.extract_metadata = staticmethod(failing_extract)

    try:
        obj = CustomTestObject("emergency_test")
        meta = dispatch_adapter(obj)

        # Should get emergency metadata
        assert "adapter_used" in meta
        assert "emergency fallback" in meta["adapter_used"]
        assert "GenericAdapter" in meta["adapter_used"]

        # Should have warning about failure
        # Note: When GenericAdapter is the selected adapter (not a fallback),
        # there's only one error message
        assert "warnings" in meta
        warnings_text = " ".join(meta["warnings"])
        assert "GenericAdapter failed" in warnings_text

        # Should still have basic info
        assert "object_type" in meta
        assert "CustomTestObject" in meta["object_type"]

        # Should have raw_repr or placeholder
        assert "raw_repr" in meta

    finally:
        # Restore original GenericAdapter
        GenericAdapter.extract_metadata = original_extract


def test_dispatch_emergency_fallback_repr_fails():
    """Test emergency fallback when even repr() fails."""

    class UnrepresentableObject:
        def __repr__(self):
            raise RuntimeError("repr failed!")

    # Save original extract_metadata
    original_extract = GenericAdapter.extract_metadata

    # Mock GenericAdapter to fail
    def failing_extract(obj):
        raise RuntimeError("GenericAdapter failed")

    GenericAdapter.extract_metadata = staticmethod(failing_extract)

    try:
        obj = UnrepresentableObject()
        meta = dispatch_adapter(obj)

        # Should get emergency metadata
        assert "adapter_used" in meta
        assert "emergency fallback" in meta["adapter_used"]

        # Should have placeholder for failed repr
        assert "raw_repr" in meta
        assert meta["raw_repr"] == "<repr failed>"

    finally:
        # Restore original GenericAdapter
        GenericAdapter.extract_metadata = original_extract


def test_full_api_with_adapter_failure():
    """Test that api.is_() handles adapter failures gracefully."""
    # Register broken adapter at the BEGINNING
    AdapterRegistry._adapters.insert(0, BrokenAdapter)

    try:
        obj = CustomTestObject("api_test")

        # Should not crash, should return a result
        result = pls.describe(obj)

        assert result is not None
        assert result.content is not None
        assert result.meta is not None

        # Meta should contain fallback information
        assert "adapter_used" in result.meta
        assert "GenericAdapter" in result.meta["adapter_used"]
        assert "BrokenAdapter" in result.meta["adapter_used"]

        # Should have warnings
        assert "warnings" in result.meta
        assert len(result.meta["warnings"]) > 0

    finally:
        AdapterRegistry._adapters = [
            a for a in AdapterRegistry._adapters if a != BrokenAdapter
        ]


def test_successful_adapter_unchanged():
    """Test that successful adapters work normally (regression test)."""
    # Test with a simple built-in type
    obj = [1, 2, 3, 4, 5]

    meta = dispatch_adapter(obj)

    # Should use the normal adapter (CollectionsAdapter)
    assert "adapter_used" in meta
    assert "CollectionsAdapter" in meta["adapter_used"]

    # Should NOT have fallback or emergency indicators
    assert "failed" not in meta["adapter_used"]
    assert "emergency" not in meta["adapter_used"]

    # Should not have warnings from fallback
    warnings = meta.get("warnings", [])
    assert not any("failed" in str(w) for w in warnings)


def test_generic_adapter_direct_use():
    """Test GenericAdapter works normally when selected directly."""

    class UnknownObject:
        def __init__(self):
            self.data = "test"

    obj = UnknownObject()
    meta = dispatch_adapter(obj)

    # Should use GenericAdapter directly (not as fallback)
    assert meta["adapter_used"] == "GenericAdapter"

    # Should NOT have warnings about failures
    warnings = meta.get("warnings", [])
    assert not any("failed" in str(w) for w in warnings)


def test_adapter_error_message_preserved():
    """Test that original error messages are preserved in warnings."""

    class SpecificErrorAdapter:
        @staticmethod
        def can_handle(obj): return isinstance(obj, CustomTestObject)

        @staticmethod
        def extract_metadata(obj):
            raise ValueError("Specific error: version 2.0.0 required, found 1.5.0")

    # Register at the BEGINNING
    AdapterRegistry._adapters.insert(0, SpecificErrorAdapter)

    try:
        obj = CustomTestObject()
        meta = dispatch_adapter(obj)

        # Error message should be in warnings
        assert "warnings" in meta
        warnings_text = " ".join(meta["warnings"])
        assert "version 2.0.0 required" in warnings_text
        assert "found 1.5.0" in warnings_text

    finally:
        AdapterRegistry._adapters = [
            a for a in AdapterRegistry._adapters if a != SpecificErrorAdapter
        ]


def test_multiple_adapter_failures_in_sequence():
    """Test that fallback system handles multiple different failures."""

    class FirstObject:
        pass

    class SecondObject:
        pass

    class FirstAdapter:
        @staticmethod
        def can_handle(obj): return isinstance(obj, FirstObject)

        @staticmethod
        def extract_metadata(obj):
            raise RuntimeError("First adapter failed")

    class SecondAdapter:
        @staticmethod
        def can_handle(obj): return isinstance(obj, SecondObject)

        @staticmethod
        def extract_metadata(obj):
            raise AttributeError("Second adapter failed")

    # Register at the BEGINNING
    AdapterRegistry._adapters.insert(0, FirstAdapter)
    AdapterRegistry._adapters.insert(0, SecondAdapter)

    try:
        # Test first object
        obj1 = FirstObject()
        meta1 = dispatch_adapter(obj1)
        assert "GenericAdapter" in meta1["adapter_used"]
        assert any("First adapter failed" in w for w in meta1.get("warnings", []))

        # Test second object
        obj2 = SecondObject()
        meta2 = dispatch_adapter(obj2)
        assert "GenericAdapter" in meta2["adapter_used"]
        assert any("Second adapter failed" in w for w in meta2.get("warnings", []))

    finally:
        AdapterRegistry._adapters = [
            a
            for a in AdapterRegistry._adapters
            if a not in (FirstAdapter, SecondAdapter)
        ]
