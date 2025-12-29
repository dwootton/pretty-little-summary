"""Tests for core module."""

import os

import pytest

from pretty_little_summary.core import Config, HistorySlicer, configure


def test_config_singleton():
    """Config returns same instance."""
    config1 = Config.get_instance()
    config2 = Config.get_instance()
    assert config1 is config2


def test_config_update():
    """Config update works correctly."""
    config = Config.get_instance()
    config.update(openrouter_api_key="new-key", model="new-model")
    assert config.openrouter_api_key == "new-key"
    assert config.openrouter_model == "new-model"


def test_configure_function():
    """configure() function updates config."""
    configure(openrouter_api_key="test-key", max_history_lines=20)
    config = Config.get_instance()
    assert config.openrouter_api_key == "test-key"
    assert config.max_history_lines == 20


def test_history_slicer_standard_python():
    """HistorySlicer returns None in standard Python."""
    # In standard Python (not IPython), should return None
    result = HistorySlicer.get_history(var_name="test")
    assert result is None


def test_history_slicer_is_ipython_environment():
    """HistorySlicer.is_ipython_environment() returns False in standard Python."""
    assert HistorySlicer.is_ipython_environment() is False


def test_history_filtering():
    """HistorySlicer filters history by variable name."""
    history = [
        "import pandas as pd",
        "df = pd.read_csv('data.csv')",
        "x = 10",
        "df.head()",
        "print(df)",
    ]

    filtered = HistorySlicer._filter_history(history, "df")

    assert len(filtered) == 3
    assert "df = pd.read_csv('data.csv')" in filtered
    assert "df.head()" in filtered
    assert "print(df)" in filtered
    assert "x = 10" not in filtered
