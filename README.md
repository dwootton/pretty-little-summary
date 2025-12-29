# Vibe Check

**Natural language summaries of Python objects for LLM consumption.**

Vibe Check bridges the gap between raw Python objects and LLM context by combining **introspection** (what the object is now) with **narrative provenance** (how it was created). Perfect for Jupyter notebooks and data science workflows.

## Features

- 🎯 **Single function API**: Just call `vibe.check(obj)`
- 🧠 **LLM-powered explanations**: Natural language summaries via OpenRouter
- ⚡ **Deterministic mode**: Fast summaries without API calls (`explain=False`)
- 📊 **10+ library adapters**: pandas, polars, matplotlib, altair, sklearn, pytorch, xarray, pydantic, networkx, requests
- 📜 **History tracking**: Captures your Jupyter notebook code context
- 🔌 **Extensible**: Register custom adapters for your types
- 🛡️ **Graceful degradation**: No hard dependencies on data libraries

## Installation

```bash
# Using uv (recommended)
uv pip install vibe-check

# Using pip
pip install vibe-check
```

## Quick Start

```python
import vibe_check as vibe
import pandas as pd

# Configure (or use OPENROUTER_API_KEY environment variable)
vibe.configure(openrouter_api_key="sk-or-...")

# Load some data
df = pd.read_csv("sales_data.csv")

# Option 1: Get LLM explanation (default)
result = vibe.check(df)
print(result.content)
# "This DataFrame contains 1,000 rows of sales data across 5 columns including
#  product names, prices, quantities, dates, and customer IDs. The data appears
#  to span Q1-Q4 2024 with a focus on retail transactions."

print(result.meta)
# {'object_type': 'pandas.DataFrame', 'shape': (1000, 5),
#  'columns': ['product', 'price', 'quantity', 'date', 'customer_id'], ...}

print(result.history)
# ['df = pd.read_csv("sales_data.csv")', ...]

# Option 2: Get deterministic summary (no LLM, no API call)
result = vibe.check(df, explain=False)
print(result.content)
# "pandas.DataFrame | Shape: (1000, 5) | Columns: product, price, quantity, date, customer_id | [via PandasAdapter]"
```

## Configuration

### Environment Variables

Create a `.env` file:

```bash
OPENROUTER_API_KEY=sk-or-your-key-here
VIBECHECK_MODEL=anthropic/claude-3.5-sonnet  # Optional: override default
VIBECHECK_MAX_HISTORY=10                     # Optional: max history lines
VIBECHECK_DEBUG=false                        # Optional: debug mode
```

### Programmatic Configuration

```python
import vibe_check as vibe

vibe.configure(
    openrouter_api_key="sk-or-...",
    model="anthropic/claude-3.5-sonnet",  # Default model
    max_history_lines=10,                  # History context
    debug=False
)
```

## Supported Libraries

Vibe Check includes specialized adapters for:

| Library | Support | What's Extracted |
|---------|---------|------------------|
| **Pandas** | DataFrame, Series | Columns, dtypes, shape, sample rows |
| **Polars** | DataFrame, LazyFrame | Schema, shape, optimized query plan |
| **Matplotlib** | Figure, Axes | Titles, labels, legend, plot type (via history) |
| **Altair** | Chart | Vega-Lite spec, mark type, encoding |
| **Scikit-Learn** | Models | Hyperparameters, fitted status, features |
| **PyTorch** | nn.Module | Architecture, parameter count, device |
| **Xarray** | DataArray, Dataset | Dimensions, coordinates, attributes |
| **Pydantic** | BaseModel | JSON schema, fields, current values |
| **NetworkX** | Graph | Node/edge counts, density, sample nodes |
| **Requests** | Response | Status code, URL, headers, JSON keys |
| **Generic** | Any object | Type info, repr, attributes (fallback) |

## API Reference

### `check(obj, explain=True, name=None)`

Generate a summary of any Python object.

**Parameters:**
- `obj` (Any): Object to analyze
- `explain` (bool): If True, use LLM for natural language summary. If False, return deterministic summary. Default: True
- `name` (str, optional): Variable name for history filtering. Auto-detected in Jupyter if not provided.

**Returns:**
- `VibeCheck`: Object with three attributes:
  - `content` (str): Natural language summary
  - `meta` (dict): Structured metadata
  - `history` (list[str] | None): Code history from Jupyter (if available)

**Raises:**
- `ConfigurationError`: If API key not set and `explain=True`
- `APIError`: If LLM synthesis fails

### `configure(**kwargs)`

Configure vibe_check settings.

**Parameters:**
- `openrouter_api_key` (str, optional): OpenRouter API key
- `model` (str, optional): LLM model to use (default: "anthropic/claude-3.5-sonnet")
- `max_history_lines` (int, optional): Max history lines to include (default: 10)
- `debug` (bool, optional): Enable debug logging (default: False)

### `VibeCheck` (dataclass)

Result object from `check()`.

**Attributes:**
- `content` (str): The natural language summary (the "Vibe")
- `meta` (dict): Structured facts (schema, stats, adapter used)
- `history` (list[str] | None): Code history if running in Jupyter

## Examples

### Basic DataFrame Analysis

```python
import pandas as pd
import vibe_check as vibe

vibe.configure(openrouter_api_key="sk-or-...")

# Create sample data
df = pd.DataFrame({
    'name': ['Alice', 'Bob', 'Charlie'],
    'age': [25, 30, 35],
    'salary': [50000, 60000, 70000]
})

result = vibe.check(df)
print(result.content)
# "This DataFrame contains employee data with 3 rows and 3 columns:
#  names, ages, and salaries. The ages range from 25-35 and salaries
#  from $50k-$70k."
```

### Matplotlib Visualization

```python
import matplotlib.pyplot as plt
import vibe_check as vibe

fig, ax = plt.subplots()
ax.plot([1, 2, 3], [1, 4, 9])
ax.set_title("Quadratic Growth")
ax.set_xlabel("X")
ax.set_ylabel("Y")

result = vibe.check(fig)
print(result.content)
# Uses the plot creation history to understand intent:
# "This matplotlib figure shows a quadratic growth curve with labeled
#  axes. The plot visualizes the relationship y = x² with 3 data points."
```

### Scikit-Learn Model

```python
from sklearn.ensemble import RandomForestClassifier
import vibe_check as vibe

model = RandomForestClassifier(n_estimators=100, max_depth=5)
# ... train model ...

result = vibe.check(model)
print(result.content)
# "This is a fitted Random Forest classifier with 100 trees and max depth
#  of 5. It was trained on data with 10 features and 3 classes."
```

### Deterministic Mode (No LLM)

```python
import vibe_check as vibe
import pandas as pd

df = pd.read_csv("data.csv")

# Fast, structured summary without API call
result = vibe.check(df, explain=False)
print(result.content)
# "pandas.DataFrame | Shape: (500, 8) | Columns: id, name, date, value, category, ... | [via PandasAdapter]"

# Access structured metadata
print(result.meta['shape'])  # (500, 8)
print(result.meta['columns'])  # ['id', 'name', 'date', ...]
```

## Architecture

Vibe Check has three main components:

1. **Adapters** (Introspection Layer)
   - Detect object types using `isinstance` checks
   - Extract structured metadata (schema, stats, etc.)
   - No hard dependencies - gracefully skip unavailable libraries

2. **History Slicer** (Narrative Provenance)
   - Detects IPython/Jupyter environment
   - Extracts relevant code history
   - Filters by variable name

3. **Synthesizer** (LLM Integration)
   - Combines metadata + history into LLM prompt
   - Calls OpenRouter API
   - Falls back to deterministic summary on error

## Development

```bash
# Clone repository
git clone https://github.com/yourusername/vibe_check.git
cd vibe_check

# Install with dev dependencies
uv pip install -e ".[dev]"

# Run tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=vibe_check --cov-report=html

# Type checking
uv run mypy src/vibe_check

# Linting
uv run ruff check src/vibe_check
uv run ruff format src/vibe_check

# Install all optional dependencies for testing
uv pip install -e ".[all]"
```

## Philosophy

**Why Vibe Check?**

Modern data science workflows involve passing objects between code cells, tools, and LLMs. But LLMs don't understand `<pandas.DataFrame at 0x7f8a2c3d4e50>`. They need context.

Vibe Check solves this by:

1. **Introspection**: What IS this object? (schema, shape, type)
2. **Provenance**: How was it CREATED? (code history from Jupyter)
3. **Synthesis**: What does it MEAN? (LLM explanation)

The result: Rich context that helps LLMs understand your data without bloating prompts with raw dumps.

## License

MIT License - see LICENSE file for details.

---

**Built with ❤️ for the data science community**
