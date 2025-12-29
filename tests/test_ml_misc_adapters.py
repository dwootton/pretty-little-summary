"""Tests for ML/analytics adapters."""

import pytest

from wut_is.adapters import dispatch_adapter
from wut_is.synthesizer import deterministic_summary


tf = pytest.importorskip("tensorflow")


def test_tensorflow_adapter() -> None:
    tensor = tf.constant([1.0, 2.0])
    meta = dispatch_adapter(tensor)
    assert meta["adapter_used"] == "TensorflowAdapter"
    assert meta["metadata"]["type"] == "tf_tensor"
    print("tensorflow:", deterministic_summary(meta))
    assert "TensorFlow tensor" in deterministic_summary(meta)


jax = pytest.importorskip("jax")
import jax.numpy as jnp  # noqa: E402


def test_jax_adapter() -> None:
    arr = jnp.array([1, 2, 3])
    meta = dispatch_adapter(arr)
    assert meta["adapter_used"] == "JaxAdapter"
    assert meta["metadata"]["type"] == "jax_array"
    print("jax:", deterministic_summary(meta))
    assert "JAX array" in deterministic_summary(meta)


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
    print("statsmodels:", deterministic_summary(meta))
    assert "statsmodels results object" in deterministic_summary(meta)


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
    assert "sklearn Pipeline" in summary
