"""Adapter system for wut_is."""

from wut_is.adapters._base import Adapter, AdapterRegistry, dispatch_adapter

# Import specialized adapters FIRST (before GenericAdapter)
# They will be registered in import order and checked in that order
# GenericAdapter MUST be imported last so it's lowest priority (fallback)

# Optional adapters - import attempts, silently skips if library unavailable
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
    from wut_is.adapters.sklearn import SklearnAdapter
except ImportError:
    pass

try:
    from wut_is.adapters.pytorch import PytorchAdapter
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

# Import GenericAdapter LAST (fallback adapter, lowest priority)
from wut_is.adapters.generic import GenericAdapter

__all__ = ["Adapter", "AdapterRegistry", "dispatch_adapter", "GenericAdapter"]
