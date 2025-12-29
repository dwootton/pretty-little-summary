#!/usr/bin/env python3
"""Helper script to split adapters.py into individual modules."""

import re
from pathlib import Path


def extract_adapter_classes(content: str) -> dict[str, str]:
    """Extract each adapter class with its implementation."""
    adapters = {}

    # Pattern to match adapter class definitions
    pattern = r'(class (\w+Adapter):\s+""".*?""".*?)(?=\n\nclass |\n\n# =====|$)'

    matches = re.findall(pattern, content, re.DOTALL)

    for match, name in matches:
        if name != "GenericAdapter":  # Skip Generic, already handled
            adapters[name] = match

    return adapters


def create_adapter_module(adapter_name: str, adapter_code: str, library_name: str) -> str:
    """Create a complete adapter module with imports and auto-registration."""

    # Detect which library this adapter uses
    library_check = ""
    if "pandas" in adapter_code.lower():
        library_check = """try:
    import pandas as pd
    LIBRARY_AVAILABLE = True
except ImportError:
    LIBRARY_AVAILABLE = False
    pd = None  # type: ignore"""
    elif "polars" in adapter_code.lower():
        library_check = """try:
    import polars as pl
    LIBRARY_AVAILABLE = True
except ImportError:
    LIBRARY_AVAILABLE = False
    pl = None  # type: ignore"""
    elif "matplotlib" in adapter_code.lower():
        library_check = """try:
    import matplotlib.figure
    import matplotlib.axes
    LIBRARY_AVAILABLE = True
except ImportError:
    LIBRARY_AVAILABLE = False"""
    elif "altair" in adapter_code.lower():
        library_check = """try:
    import altair
    LIBRARY_AVAILABLE = True
except ImportError:
    LIBRARY_AVAILABLE = False"""
    elif "sklearn" in adapter_code.lower() or "fit" in adapter_code and "get_params" in adapter_code:
        library_check = """# Sklearn detection via hasattr
LIBRARY_AVAILABLE = True  # No import needed, duck typing"""
    elif "torch" in adapter_code.lower() or "nn.Module" in adapter_code:
        library_check = """try:
    import torch.nn as nn
    LIBRARY_AVAILABLE = True
except ImportError:
    LIBRARY_AVAILABLE = False
    nn = None  # type: ignore"""
    elif "xarray" in adapter_code.lower():
        library_check = """try:
    import xarray as xr
    LIBRARY_AVAILABLE = True
except ImportError:
    LIBRARY_AVAILABLE = False
    xr = None  # type: ignore"""
    elif "pydantic" in adapter_code.lower() or "BaseModel" in adapter_code:
        library_check = """try:
    from pydantic import BaseModel
    LIBRARY_AVAILABLE = True
except ImportError:
    LIBRARY_AVAILABLE = False
    BaseModel = None  # type: ignore"""
    elif "networkx" in adapter_code.lower():
        library_check = """try:
    import networkx as nx
    LIBRARY_AVAILABLE = True
except ImportError:
    LIBRARY_AVAILABLE = False
    nx = None  # type: ignore"""
    elif "requests" in adapter_code.lower() or "Response" in adapter_code:
        library_check = """try:
    import requests
    LIBRARY_AVAILABLE = True
except ImportError:
    LIBRARY_AVAILABLE = False
    requests = None  # type: ignore"""

    # Replace can_handle to check LIBRARY_AVAILABLE
    adapter_code_modified = adapter_code

    # Create module content
    module = f'''"""{adapter_name} for {library_name}."""

from typing import Any

{library_check}

from vibe_check.adapters._base import Adapter, AdapterRegistry
from vibe_check.core import MetaDescription


{adapter_code_modified}


# Auto-register if library is available
if LIBRARY_AVAILABLE:
    AdapterRegistry.register({adapter_name})
'''

    return module


# Read original file
src_file = Path("src/vibe_check/adapters.py")
content = src_file.read_text()

# Extract adapters
adapters = extract_adapter_classes(content)

print(f"Found {len(adapters)} adapters:")
for name in adapters.keys():
    print(f"  - {name}")

# Print adapter names and approximate line counts
for name, code in adapters.items():
    lines = len(code.split('\n'))
    print(f"{name}: {lines} lines")
