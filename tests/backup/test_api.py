"""Tests for main API."""

from unittest.mock import Mock, patch

import pytest

from pretty_little_summary.api import Description, describe
from pretty_little_summary.core import ConfigurationError


def test_description_dataclass():
    """Description dataclass works correctly."""
    result = Description(
        content="Test summary", meta={"object_type": "test"}, history=["line 1"]
    )

    assert result.content == "Test summary"
    assert result.meta["object_type"] == "test"
    assert result.history == ["line 1"]


@patch("pretty_little_summary.api.dispatch_adapter")
@patch("pretty_little_summary.api.HistorySlicer")
def test_check_explain_false(mock_history, mock_dispatch):
    """describe() with explain=False uses deterministic summary."""
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
    result = describe(obj, explain=False)

    assert isinstance(result, Description)
    assert "pandas.DataFrame" in result.content
    assert "Shape: (10, 3)" in result.content
    assert result.meta["object_type"] == "pandas.DataFrame"


@patch("pretty_little_summary.api.OpenRouterClient")
@patch("pretty_little_summary.api.dispatch_adapter")
@patch("pretty_little_summary.api.HistorySlicer")
@patch("pretty_little_summary.api.Config")
def test_is_explain_true(mock_config_class, mock_history, mock_dispatch, mock_client_class):
    """describe() with explain=True calls LLM."""
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
    result = describe(obj, explain=True)

    assert isinstance(result, Description)
    assert result.content == "LLM generated summary"
    mock_client.synthesize.assert_called_once()


@patch("pretty_little_summary.api.Config")
def test_is_no_api_key_raises_error(mock_config_class):
    """describe() with explain=True and no API key raises ConfigurationError."""
    # Mock config without API key
    mock_config = Mock()
    mock_config.openrouter_api_key = None
    mock_config_class.get_instance.return_value = mock_config

    obj = {"test": "data"}

    with pytest.raises(ConfigurationError):
        describe(obj, explain=True)


@patch("pretty_little_summary.api.dispatch_adapter")
@patch("pretty_little_summary.api.HistorySlicer")
def test_is_includes_history(mock_history, mock_dispatch):
    """describe() includes history when available."""
    # Mock adapter
    mock_dispatch.return_value = {
        "object_type": "test",
        "adapter_used": "GenericAdapter",
    }

    # Mock history
    mock_history.is_ipython_environment.return_value = True
    mock_history.get_history.return_value = ["line 1", "line 2"]

    obj = {"test": "data"}
    result = describe(obj, explain=False)

    assert result.history == ["line 1", "line 2"]
    mock_history.get_history.assert_called_once()
