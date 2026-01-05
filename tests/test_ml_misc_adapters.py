"""Tests for ML/analytics adapters."""

import pytest

from pretty_little_summary.adapters import dispatch_adapter
from pretty_little_summary.synthesizer import deterministic_summary
from tests.input import build_input, expected_output, load_example


tf = pytest.importorskip("tensorflow")


def test_tensorflow_adapter() -> None:
    example = load_example("tensorflow_adapter")
    meta = dispatch_adapter(build_input(example))
    assert meta["adapter_used"] == "TensorflowAdapter"
    assert meta["metadata"]["type"] == "tf_tensor"
    summary = deterministic_summary(meta)
    print("tensorflow:", summary)
    assert summary == expected_output(example, meta)


jax = pytest.importorskip("jax")


def test_jax_adapter() -> None:
    example = load_example("jax_adapter")
    meta = dispatch_adapter(build_input(example))
    assert meta["adapter_used"] == "JaxAdapter"
    assert meta["metadata"]["type"] == "jax_array"
    summary = deterministic_summary(meta)
    print("jax:", summary)
    assert summary == expected_output(example, meta)


statsmodels = pytest.importorskip("statsmodels.api")


def test_statsmodels_adapter() -> None:
    example = load_example("statsmodels_adapter")
    meta = dispatch_adapter(build_input(example))
    assert meta["adapter_used"] == "StatsmodelsAdapter"
    assert meta["metadata"]["type"] == "statsmodels_result"
    summary = deterministic_summary(meta)
    print("statsmodels:", summary)
    assert summary == expected_output(example, meta)


sklearn = pytest.importorskip("sklearn")


def test_sklearn_pipeline_adapter() -> None:
    example = load_example("sklearn_pipeline_adapter")
    meta = dispatch_adapter(build_input(example))
    assert meta["adapter_used"] == "SklearnPipelineAdapter"
    summary = deterministic_summary(meta)
    print("sklearn_pipeline:", summary)
    assert summary == expected_output(example, meta)
