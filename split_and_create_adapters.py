#!/usr/bin/env python3
"""Helper script to split adapters.py into individual modules."""

import re
from pathlib import Path


# Read original file
src_file = Path("src/vibe_check/adapters.py")
content = src_file.read_text()

# Define adapter configurations
ADAPTER_CONFIGS = {
    "PandasAdapter": {
        "library": "pandas",
        "import": "import pandas as pd",
        "check": "isinstance(obj, (pd.DataFrame, pd.Series))",
    },
    "PolarsAdapter": {
        "library": "polars",
        "import": "import polars as pl",
        "check": "isinstance(obj, (pl.DataFrame, pl.LazyFrame))",
    },
    "MatplotlibAdapter": {
        "library": "matplotlib",
        "import": "import matplotlib.figure\\nimport matplotlib.axes",
        "check": "isinstance(obj, (matplotlib.figure.Figure, matplotlib.axes.Axes))",
    },
    "AltairAdapter": {
        "library": "altair",
        "import": "import altair",
        "check": "isinstance(obj, altair.Chart)",
    },
    "SklearnAdapter": {
        "library": "sklearn",
        "import": "# Sklearn uses duck typing",
        "check": "hasattr(obj, 'get_params') and hasattr(obj, 'fit')",
    },
    "PytorchAdapter": {
        "library": "pytorch",
        "import": "import torch.nn as nn",
        "check": "isinstance(obj, nn.Module)",
    },
    "XarrayAdapter": {
        "library": "xarray",
        "import": "import xarray as xr",
        "check": "isinstance(obj, (xr.DataArray, xr.Dataset))",
    },
    "PydanticAdapter": {
        "library": "pydantic",
        "import": "from pydantic import BaseModel",
        "check": "isinstance(obj, BaseModel)",
    },
    "NetworkXAdapter": {
        "library": "networkx",
        "import": "import networkx as nx",
        "check": "isinstance(obj, nx.Graph)",
    },
    "RequestsAdapter": {
        "library": "requests",
        "import": "import requests",
        "check": "isinstance(obj, requests.Response)",
    },
}

# Extract each adapter class
for adapter_name, config in ADAPTER_CONFIGS.items():
    # Find the adapter class in the original file
    pattern = f"class {adapter_name}:.*?(?=\n\nclass |\n\n# =====|$)"
    match = re.search(pattern, content, re.DOTALL)

    if not match:
        print(f"Could not find {adapter_name}")
        continue

    adapter_code = match.group(0)

    # Extract just the class body (methods)
    # We'll rebuild can_handle with LIBRARY_AVAILABLE check
    extract_methods_pattern = r"@staticmethod\s+def extract_metadata.*"
    extract_match = re.search(extract_methods_pattern, adapter_code, re.DOTALL)

    if not extract_match:
        print(f"Could not extract methods for {adapter_name}")
        continue

    extract_method = extract_match.group(0)

    # Build module content
    library_name = config["library"]
    import_stmt = config["import"]

    # Special handling for sklearn (no try/except needed)
    if library_name == "sklearn":
        library_check = "# Sklearn uses duck typing, no import check needed\nLIBRARY_AVAILABLE = True"
    else:
        library_check = f'''try:
    {import_stmt}
    LIBRARY_AVAILABLE = True
except ImportError:
    LIBRARY_AVAILABLE = False'''

    # Create can_handle method
    can_handle_code = f"""    @staticmethod
    def can_handle(obj: Any) -> bool:
        if not LIBRARY_AVAILABLE:
            return False
        try:
            return {config["check"]}
        except Exception:
            return False"""

    # Create file content
    file_name = library_name.lower() if library_name != "pytorch" else "pytorch"
    if library_name == "sklearn":
        file_name = "sklearn"

    module_content = f'''"""{adapter_name.replace("Adapter", "")} adapter."""

from typing import Any

{library_check}

from vibe_check.adapters._base import AdapterRegistry
from vibe_check.core import MetaDescription


class {adapter_name}:
    """{adapter_code.split('"""')[1].split('"""')[0]}"""

{can_handle_code}

    {extract_method}


# Auto-register if library is available
if LIBRARY_AVAILABLE:
    AdapterRegistry.register({adapter_name})
'''

    # Write file
    output_file = Path(f"src/vibe_check/adapters/{file_name}.py")
    output_file.write_text(module_content)
    print(f"Created {output_file}")

print("All adapter files created!")
