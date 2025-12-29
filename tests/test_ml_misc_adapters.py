"""Tests for ML/analytics adapters."""

import pytest

from pretty_little_summary.adapters import dispatch_adapter
from pretty_little_summary.synthesizer import deterministic_summary


tf = pytest.importorskip("tensorflow")


def test_tensorflow_adapter() -> None:
    tensor = tf.constant([1.0, 2.0])
    meta = dispatch_adapter(tensor)
    assert meta["adapter_used"] == "TensorflowAdapter"
    assert meta["metadata"]["type"] == "tf_tensor"
    summary = deterministic_summary(meta)
    print("tensorflow:", summary)
    assert summary == "A TensorFlow tensor with shape (2,)."


jax = pytest.importorskip("jax")
import jax.numpy as jnp  # noqa: E402


def test_jax_adapter() -> None:
    arr = jnp.array([1, 2, 3])
    meta = dispatch_adapter(arr)
    assert meta["adapter_used"] == "JaxAdapter"
    assert meta["metadata"]["type"] == "jax_array"
    summary = deterministic_summary(meta)
    print("jax:", summary)
    assert summary == "A JAX array with shape (3,)."


statsmodels = pytest.importorskip("statsmodels.api")
import statsmodels.api as sm  # noqa: E402
import numpy as np  # noqa: E402


def test_statsmodels_adapter() -> None:
    x = np.arange(10)
    y = x * 2
    x = sm.add_constant(x)
    model = sm.OLS(y, x).fit()
    meta = dispatch_adapter(model)
    assert meta["adapter_used"] == "StatsmodelsAdapter"
    assert meta["metadata"]["type"] == "statsmodels_result"
    summary = deterministic_summary(meta)
    print("statsmodels:", summary)
    assert summary == "A statsmodels results object RegressionResultsWrapper."


sklearn = pytest.importorskip("sklearn")
from sklearn.impute import SimpleImputer  # noqa: E402
from sklearn.pipeline import Pipeline  # noqa: E402
from sklearn.preprocessing import StandardScaler  # noqa: E402


def test_sklearn_pipeline_adapter() -> None:
    pipe = Pipeline(
        [
            ("imputer", SimpleImputer()),
            ("scaler", StandardScaler()),
        ]
    )
    meta = dispatch_adapter(pipe)
    assert meta["adapter_used"] == "SklearnPipelineAdapter"
    summary = deterministic_summary(meta)
    print("sklearn_pipeline:", summary)
    assert summary == (
        "A unfitted sklearn Pipeline with 2 steps:\n"
        "1. 'imputer': SimpleImputer\n"
        "2. 'scaler': StandardScaler\n"
        "Expects input shape (*, ?), outputs class predictions."
    )
