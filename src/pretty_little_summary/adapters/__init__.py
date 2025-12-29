"""Adapter system for pretty_little_summary."""

from pretty_little_summary.adapters._base import (
    Adapter,
    AdapterRegistry,
    dispatch_adapter,
    list_available_adapters,
)

# Import specialized adapters FIRST (before GenericAdapter)
# They will be registered in import order and checked in that order
# GenericAdapter MUST be imported last so it's lowest priority (fallback)

# Optional adapters - import attempts, silently skips if library unavailable
try:
    from pretty_little_summary.adapters.text_formats import TextFormatAdapter
except ImportError:
    pass

try:
    from pretty_little_summary.adapters.primitives import PrimitiveAdapter
except ImportError:
    pass

try:
    from pretty_little_summary.adapters.pandas import PandasAdapter
except ImportError:
    pass

try:
    from pretty_little_summary.adapters.polars import PolarsAdapter
except ImportError:
    pass

try:
    from pretty_little_summary.adapters.matplotlib import MatplotlibAdapter
except ImportError:
    pass

try:
    from pretty_little_summary.adapters.altair import AltairAdapter
except ImportError:
    pass

try:
    from pretty_little_summary.adapters.seaborn_adapter import SeabornAdapter
except ImportError:
    pass

try:
    from pretty_little_summary.adapters.plotly_adapter import PlotlyAdapter
except ImportError:
    pass

try:
    from pretty_little_summary.adapters.bokeh_adapter import BokehAdapter
except ImportError:
    pass

try:
    from pretty_little_summary.adapters.sklearn_pipeline import SklearnPipelineAdapter
except ImportError:
    pass

try:
    from pretty_little_summary.adapters.sklearn import SklearnAdapter
except ImportError:
    pass

try:
    from pretty_little_summary.adapters.statsmodels_adapter import StatsmodelsAdapter
except ImportError:
    pass

try:
    from pretty_little_summary.adapters.numpy_adapter import NumpyAdapter
except ImportError:
    pass

try:
    from pretty_little_summary.adapters.scipy_sparse_adapter import ScipySparseAdapter
except ImportError:
    pass

try:
    from pretty_little_summary.adapters.pyarrow_adapter import PyArrowAdapter
except ImportError:
    pass

try:
    from pretty_little_summary.adapters.h5py_adapter import H5pyAdapter
except ImportError:
    pass

try:
    from pretty_little_summary.adapters.pil_adapter import PILAdapter
except ImportError:
    pass

try:
    from pretty_little_summary.adapters.pytorch import PytorchAdapter
except ImportError:
    pass

try:
    from pretty_little_summary.adapters.tensorflow_adapter import TensorflowAdapter
except ImportError:
    pass

try:
    from pretty_little_summary.adapters.jax_adapter import JaxAdapter
except ImportError:
    pass

try:
    from pretty_little_summary.adapters.xarray import XarrayAdapter
except ImportError:
    pass

try:
    from pretty_little_summary.adapters.pydantic import PydanticAdapter
except ImportError:
    pass

try:
    from pretty_little_summary.adapters.networkx import NetworkXAdapter
except ImportError:
    pass

try:
    from pretty_little_summary.adapters.requests import RequestsAdapter
except ImportError:
    pass

# Stdlib adapters
try:
    from pretty_little_summary.adapters.datetime_adapter import DateTimeAdapter
except ImportError:
    pass

try:
    from pretty_little_summary.adapters.pathlib_adapter import PathlibAdapter
except ImportError:
    pass

try:
    from pretty_little_summary.adapters.regex_adapter import RegexAdapter
except ImportError:
    pass

try:
    from pretty_little_summary.adapters.uuid_adapter import UUIDAdapter
except ImportError:
    pass

try:
    from pretty_little_summary.adapters.io_adapter import IOAdapter
except ImportError:
    pass

try:
    from pretty_little_summary.adapters.attrs_adapter import AttrsAdapter
except ImportError:
    pass

try:
    from pretty_little_summary.adapters.ipython_display import IPythonDisplayAdapter
except ImportError:
    pass

try:
    from pretty_little_summary.adapters.structured import StructuredAdapter
except ImportError:
    pass

try:
    from pretty_little_summary.adapters.callables import CallableAdapter
except ImportError:
    pass

try:
    from pretty_little_summary.adapters.async_adapter import AsyncAdapter
except ImportError:
    pass

try:
    from pretty_little_summary.adapters.errors import ErrorAdapter
except ImportError:
    pass

# Core collections (after specialized adapters to avoid shadowing)
try:
    from pretty_little_summary.adapters.collections import CollectionsAdapter
except ImportError:
    pass

# Import GenericAdapter LAST (fallback adapter, lowest priority)
from pretty_little_summary.adapters.generic import GenericAdapter

__all__ = [
    "Adapter",
    "AdapterRegistry",
    "dispatch_adapter",
    "list_available_adapters",
    "GenericAdapter",
]
