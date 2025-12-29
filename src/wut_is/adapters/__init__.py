"""Adapter system for wut_is."""

from wut_is.adapters._base import Adapter, AdapterRegistry, dispatch_adapter

# Import specialized adapters FIRST (before GenericAdapter)
# They will be registered in import order and checked in that order
# GenericAdapter MUST be imported last so it's lowest priority (fallback)

# Optional adapters - import attempts, silently skips if library unavailable
try:
    from wut_is.adapters.text_formats import TextFormatAdapter
except ImportError:
    pass

try:
    from wut_is.adapters.primitives import PrimitiveAdapter
except ImportError:
    pass

try:
    from wut_is.adapters.pandas import PandasAdapter
except ImportError:
    pass

try:
    from wut_is.adapters.polars import PolarsAdapter
except ImportError:
    pass

try:
    from wut_is.adapters.matplotlib import MatplotlibAdapter
except ImportError:
    pass

try:
    from wut_is.adapters.altair import AltairAdapter
except ImportError:
    pass

try:
    from wut_is.adapters.seaborn_adapter import SeabornAdapter
except ImportError:
    pass

try:
    from wut_is.adapters.plotly_adapter import PlotlyAdapter
except ImportError:
    pass

try:
    from wut_is.adapters.bokeh_adapter import BokehAdapter
except ImportError:
    pass

try:
    from wut_is.adapters.sklearn_pipeline import SklearnPipelineAdapter
except ImportError:
    pass

try:
    from wut_is.adapters.sklearn import SklearnAdapter
except ImportError:
    pass

try:
    from wut_is.adapters.statsmodels_adapter import StatsmodelsAdapter
except ImportError:
    pass

try:
    from wut_is.adapters.numpy_adapter import NumpyAdapter
except ImportError:
    pass

try:
    from wut_is.adapters.scipy_sparse_adapter import ScipySparseAdapter
except ImportError:
    pass

try:
    from wut_is.adapters.pyarrow_adapter import PyArrowAdapter
except ImportError:
    pass

try:
    from wut_is.adapters.h5py_adapter import H5pyAdapter
except ImportError:
    pass

try:
    from wut_is.adapters.pil_adapter import PILAdapter
except ImportError:
    pass

try:
    from wut_is.adapters.pytorch import PytorchAdapter
except ImportError:
    pass

try:
    from wut_is.adapters.tensorflow_adapter import TensorflowAdapter
except ImportError:
    pass

try:
    from wut_is.adapters.jax_adapter import JaxAdapter
except ImportError:
    pass

try:
    from wut_is.adapters.xarray import XarrayAdapter
except ImportError:
    pass

try:
    from wut_is.adapters.pydantic import PydanticAdapter
except ImportError:
    pass

try:
    from wut_is.adapters.networkx import NetworkXAdapter
except ImportError:
    pass

try:
    from wut_is.adapters.requests import RequestsAdapter
except ImportError:
    pass

# Stdlib adapters
try:
    from wut_is.adapters.datetime_adapter import DateTimeAdapter
except ImportError:
    pass

try:
    from wut_is.adapters.pathlib_adapter import PathlibAdapter
except ImportError:
    pass

try:
    from wut_is.adapters.regex_adapter import RegexAdapter
except ImportError:
    pass

try:
    from wut_is.adapters.uuid_adapter import UUIDAdapter
except ImportError:
    pass

try:
    from wut_is.adapters.io_adapter import IOAdapter
except ImportError:
    pass

try:
    from wut_is.adapters.attrs_adapter import AttrsAdapter
except ImportError:
    pass

try:
    from wut_is.adapters.ipython_display import IPythonDisplayAdapter
except ImportError:
    pass

try:
    from wut_is.adapters.structured import StructuredAdapter
except ImportError:
    pass

try:
    from wut_is.adapters.callables import CallableAdapter
except ImportError:
    pass

try:
    from wut_is.adapters.async_adapter import AsyncAdapter
except ImportError:
    pass

try:
    from wut_is.adapters.errors import ErrorAdapter
except ImportError:
    pass

# Core collections (after specialized adapters to avoid shadowing)
try:
    from wut_is.adapters.collections import CollectionsAdapter
except ImportError:
    pass

# Import GenericAdapter LAST (fallback adapter, lowest priority)
from wut_is.adapters.generic import GenericAdapter

__all__ = ["Adapter", "AdapterRegistry", "dispatch_adapter", "GenericAdapter"]
