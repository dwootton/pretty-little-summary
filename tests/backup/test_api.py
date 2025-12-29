"""Tests for main API."""

from unittest.mock import Mock, patch

import pytest

from vibe_check.api import VibeCheck, check
from vibe_check.core import ConfigurationError


def test_vibecheck_dataclass():
    """VibeCheck dataclass works correctly."""
    result = VibeCheck(
        content="Test summary", meta={"object_type": "test"}, history=["line 1"]
    )

    assert result.content == "Test summary"
    assert result.meta["object_type"] == "test"
    assert result.history == ["line 1"]


@patch("vibe_check.api.dispatch_adapter")
@patch("vibe_check.api.HistorySlicer")
def test_check_explain_false(mock_history, mock_dispatch):
    """check() with explain=False uses deterministic summary."""
    # Mock adapter
    mock_dispatch.return_value = {
        "object_type": "pandas.DataFrame",
        "adapter_used": "PandasAdapter",
        "shape": (10, 3),
    }

    # Mock history
    mock_history.is_ipython_environment.return_value = False

    # Call check with explain=False (no API key needed)
    obj = {"test": "data"}
    result = check(obj, explain=False)

    assert isinstance(result, VibeCheck)
    assert "pandas.DataFrame" in result.content
    assert "Shape: (10, 3)" in result.content
    assert result.meta["object_type"] == "pandas.DataFrame"


@patch("vibe_check.api.OpenRouterClient")
@patch("vibe_check.api.dispatch_adapter")
@patch("vibe_check.api.HistorySlicer")
@patch("vibe_check.api.Config")
def test_check_explain_true(mock_config_class, mock_history, mock_dispatch, mock_client_class):
    """check() with explain=True calls LLM."""
    # Mock config
    mock_config = Mock()
    mock_config.openrouter_api_key = "test-key"
    mock_config.openrouter_model = "test-model"
    mock_config.max_history_lines = 10
    mock_config_class.get_instance.return_value = mock_config

    # Mock adapter
    mock_dispatch.return_value = {
        "object_type": "pandas.DataFrame",
        "adapter_used": "PandasAdapter",
    }

    # Mock history
    mock_history.is_ipython_environment.return_value = False

    # Mock OpenRouter client
    mock_client = Mock()
    mock_client.synthesize.return_value = "LLM generated summary"
    mock_client_class.return_value = mock_client

    # Call check with explain=True
    obj = {"test": "data"}
    result = check(obj, explain=True)

    assert isinstance(result, VibeCheck)
    assert result.content == "LLM generated summary"
    mock_client.synthesize.assert_called_once()


@patch("vibe_check.api.Config")
def test_check_no_api_key_raises_error(mock_config_class):
    """check() with explain=True and no API key raises ConfigurationError."""
    # Mock config without API key
    mock_config = Mock()
    mock_config.openrouter_api_key = None
    mock_config_class.get_instance.return_value = mock_config

    obj = {"test": "data"}

    with pytest.raises(ConfigurationError):
        check(obj, explain=True)


@patch("vibe_check.api.dispatch_adapter")
@patch("vibe_check.api.HistorySlicer")
def test_check_includes_history(mock_history, mock_dispatch):
    """check() includes history when available."""
    # Mock adapter
    mock_dispatch.return_value = {
        "object_type": "test",
        "adapter_used": "GenericAdapter",
    }

    # Mock history
    mock_history.is_ipython_environment.return_value = True
    mock_history.get_history.return_value = ["line 1", "line 2"]

    obj = {"test": "data"}
    result = check(obj, explain=False)

    assert result.history == ["line 1", "line 2"]
    mock_history.get_history.assert_called_once()
