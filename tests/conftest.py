"""Pytest fixtures for pretty_little_summary tests."""

import pytest


@pytest.fixture
def sample_dict():
    """Create a simple dictionary for testing."""
    return {"a": 1, "b": 2, "c": 3}
