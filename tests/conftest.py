"""Pytest fixtures for pretty_little_summary tests."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

sys.modules.pop("pretty_little_summary", None)


@pytest.fixture
def sample_dict():
    """Create a simple dictionary for testing."""
    return {"a": 1, "b": 2, "c": 3}
