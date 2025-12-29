"""Pytest fixtures for vibe_check tests."""

from unittest.mock import Mock

import pytest


@pytest.fixture
def mock_config():
    """Mock configuration with API key set."""
    from unittest.mock import patch

    with patch("vibe_check.core.Config.get_instance") as mock:
        config = Mock()
        config.openrouter_api_key = "test-key-123"
        config.openrouter_model = "anthropic/claude-3.5-sonnet"
        config.max_history_lines = 10
        config.debug_mode = False
        mock.return_value = config
        yield config


@pytest.fixture
def mock_openrouter_response():
    """Mock successful OpenRouter API response."""
    return {
        "choices": [{"message": {"content": "This is a test summary from the LLM."}}]
    }


@pytest.fixture
def sample_dict():
    """Create a simple dictionary for testing."""
    return {"a": 1, "b": 2, "c": 3}
