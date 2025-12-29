# Optional Dependencies Guide

## Overview

`pretty-little-summary` is designed to be **lightweight by default** while supporting a **wide range of data science libraries**. You only install what you need!

## How It Works

### Core Dependencies (Always Installed)
When you install `pretty-little-summary`, only these minimal dependencies are required:
- `httpx` - For OpenRouter API calls
- `python-dotenv` - For environment variable support

### Optional Dependencies (Installed as Needed)
Adapters for specialized libraries are **automatically activated** when those libraries are detected in your environment.

```python
import pretty_little_summary as pls

# Works immediately with built-in types
pls.describe([1, 2, 3])  # ✓ Works (no extra deps needed)

# If you already have pandas installed:
import pandas as pd
df = pd.DataFrame(...)
pls.describe(df)  # ✓ Works (PandasAdapter auto-activates)

# If pandas is NOT installed:
pls.describe(some_pandas_df)  # ✓ Still works (falls back to GenericAdapter)
```

## Installation Options

### Option 1: Minimal Install (Recommended for End Users)
If you already have your data science stack installed, just add `pretty-little-summary`:

```bash
pip install pretty-little-summary
```

The library will automatically detect and use whatever you have installed (pandas, numpy, matplotlib, etc.)

### Option 2: Install with Specific Libraries

```bash
# Data science
pip install pretty-little-summary[pandas]       # Pandas support
pip install pretty-little-summary[polars]       # Polars support
pip install pretty-little-summary[data]         # Both pandas and polars

# Visualization
pip install pretty-little-summary[matplotlib]   # Matplotlib support
pip install pretty-little-summary[altair]       # Altair support
pip install pretty-little-summary[viz]          # Both matplotlib and altair

# Machine Learning
pip install pretty-little-summary[sklearn]      # scikit-learn support
pip install pretty-little-summary[pytorch]      # PyTorch support
pip install pretty-little-summary[ml]           # Both sklearn and pytorch

# Scientific Computing
pip install pretty-little-summary[xarray]       # xarray support
pip install pretty-little-summary[networkx]     # NetworkX support
pip install pretty-little-summary[science]      # Both xarray and networkx

# Multiple groups
pip install pretty-little-summary[data,viz,ml]  # Common data science stack
```

### Option 3: Install Everything (For Development/Testing)

```bash
pip install pretty-little-summary[all]
```

This installs all optional dependencies. Only recommended for development or if you need comprehensive support.

## Checking Available Adapters

You can check which adapters are currently available based on your installed libraries:

```python
import pretty_little_summary as pls

# List all available adapters
adapters = pls.list_available_adapters()
print(adapters)
# ['PandasAdapter', 'MatplotlibAdapter', 'NumpyAdapter', ...]
```

## Supported Libraries & Their Adapters

| Library Category | Adapter | Install Extra | Always Available |
|-----------------|---------|---------------|------------------|
| **Built-in Types** | PrimitiveAdapter, CollectionsAdapter | - | ✓ |
| **Data Manipulation** | PandasAdapter | `[pandas]` | |
| | PolarsAdapter | `[polars]` | |
| | NumpyAdapter | (auto-detected) | |
| | PyArrowAdapter | (auto-detected) | |
| **Visualization** | MatplotlibAdapter | `[matplotlib]` | |
| | AltairAdapter | `[altair]` | |
| | PlotlyAdapter | (auto-detected) | |
| | SeabornAdapter | (auto-detected) | |
| | BokehAdapter | (auto-detected) | |
| **Machine Learning** | SklearnAdapter | `[sklearn]` | |
| | PytorchAdapter | `[pytorch]` | |
| | TensorflowAdapter | (auto-detected) | |
| | JaxAdapter | (auto-detected) | |
| | StatsmodelsAdapter | (auto-detected) | |
| **Scientific** | XarrayAdapter | `[xarray]` | |
| | NetworkXAdapter | `[networkx]` | |
| | ScipySparseAdapter | (auto-detected) | |
| | H5pyAdapter | (auto-detected) | |
| **Web/IO** | RequestsAdapter | `[requests]` | |
| | IPythonDisplayAdapter | `[ipython]` | |
| | PILAdapter | (auto-detected) | |
| **Stdlib** | DateTimeAdapter, PathlibAdapter, RegexAdapter, UUIDAdapter, IOAdapter | - | ✓ |
| **Data Validation** | PydanticAdapter | `[pydantic]` | |
| | AttrsAdapter | (auto-detected) | |
| **Fallback** | GenericAdapter | - | ✓ |

## For Library Developers

If you're building a library and want to use this pattern:

1. **Core dependencies only**: Keep your `dependencies` list minimal
2. **Optional dependencies**: List specialized libraries in `[project.optional-dependencies]`
3. **Lazy imports**: Use try/except at module level
4. **Runtime checks**: Check if library is available before using it

Example pattern used in `pretty-little-summary`:

```python
# At top of adapter module
try:
    import pandas as pd
    LIBRARY_AVAILABLE = True
except ImportError:
    LIBRARY_AVAILABLE = False

class PandasAdapter:
    @staticmethod
    def can_handle(obj):
        if not LIBRARY_AVAILABLE:
            return False
        return isinstance(obj, (pd.DataFrame, pd.Series))
```

## Benefits of This Approach

1. **Lightweight**: Users don't install heavy dependencies they don't need
2. **Flexible**: Works with existing installations
3. **Gradual**: Add more adapters as you install more libraries
4. **No Errors**: Missing libraries don't break functionality, just reduce adapter coverage
5. **Developer-Friendly**: Easy to test with/without specific libraries

## Troubleshooting

### "My library is installed but adapter isn't detected"

1. Check if the adapter is registered:
   ```python
   import pretty_little_summary as pls
   print(pls.list_available_adapters())
   ```

2. Verify the library is importable:
   ```python
   import pandas  # or whatever library
   ```

3. If the library imports successfully but adapter isn't listed, please file an issue!

### "I want to use a library but don't want to install via extras"

No problem! Just install the library directly:
```bash
pip install pretty-little-summary
pip install pandas  # Install pandas separately
```

`pretty-little-summary` will detect it automatically.
