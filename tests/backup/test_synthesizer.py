"""Tests for synthesizer module."""

from unittest.mock import Mock, patch

import pytest

from wut_is.core import APIError
from wut_is.synthesizer import OpenRouterClient, deterministic_summary


def test_deterministic_summary_basic():
    """deterministic_summary formats basic metadata."""
    meta = {
        "object_type": "pandas.DataFrame",
        "adapter_used": "PandasAdapter",
        "shape": (100, 5),
        "columns": ["a", "b", "c", "d", "e"],
    }

    result = deterministic_summary(meta)

    assert "pandas.DataFrame" in result
    assert "Shape: (100, 5)" in result
    assert "Columns: a, b, c, d, e" in result
    assert "PandasAdapter" in result


def test_deterministic_summary_with_many_columns():
    """deterministic_summary truncates long column lists."""
    meta = {
        "object_type": "pandas.DataFrame",
        "adapter_used": "PandasAdapter",
        "columns": [f"col{i}" for i in range(20)],
    }

    result = deterministic_summary(meta)

    assert "..." in result
    assert "(20 total)" in result


def test_deterministic_summary_graph():
    """deterministic_summary handles graph metadata."""
    meta = {
        "object_type": "networkx.Graph",
        "adapter_used": "NetworkXAdapter",
        "node_count": 50,
        "edge_count": 120,
    }

    result = deterministic_summary(meta)

    assert "Nodes: 50" in result
    assert "Edges: 120" in result


def test_deterministic_summary_ml_model():
    """deterministic_summary handles ML model metadata."""
    meta = {
        "object_type": "sklearn.RandomForestClassifier",
        "adapter_used": "SklearnAdapter",
        "parameter_count": 1000000,
        "is_fitted": True,
    }

    result = deterministic_summary(meta)

    assert "Parameters: 1,000,000" in result


@patch("httpx.post")
def test_openrouter_client_success(mock_post, mock_openrouter_response):
    """OpenRouterClient handles successful response."""
    mock_response = Mock()
    mock_response.json.return_value = mock_openrouter_response
    mock_post.return_value = mock_response

    client = OpenRouterClient(api_key="test-key", model="test-model")

    meta = {"object_type": "test", "adapter_used": "TestAdapter"}
    result = client.synthesize(meta, history=None)

    assert result == "This is a test summary from the LLM."
    mock_post.assert_called_once()


@patch("httpx.post")
def test_openrouter_client_api_error(mock_post):
    """OpenRouterClient raises APIError on HTTP error."""
    import httpx

    mock_response = Mock()
    mock_response.status_code = 500
    mock_response.text = "Internal Server Error"
    mock_post.side_effect = httpx.HTTPStatusError(
        "Error", request=Mock(), response=mock_response
    )

    client = OpenRouterClient(api_key="test-key", model="test-model")

    meta = {"object_type": "test", "adapter_used": "TestAdapter"}

    with pytest.raises(APIError):
        client.synthesize(meta, history=None)


def test_openrouter_client_builds_request_with_history():
    """OpenRouterClient includes history in request."""
    client = OpenRouterClient(api_key="test-key", model="test-model")

    meta = {"object_type": "pandas.DataFrame", "adapter_used": "PandasAdapter"}
    history = ["df = pd.read_csv('data.csv')", "df.head()"]

    request = client._build_request(meta, history)

    assert request["model"] == "test-model"
    assert len(request["messages"]) == 2
    assert "Code History" in request["messages"][0]["content"]
    assert "df.head()" in request["messages"][0]["content"]
