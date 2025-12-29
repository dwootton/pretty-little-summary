# Vibe Check Examples - Complete Guide

This guide provides notebook-ready Python examples for using the `vibe_check` library to turn any Python variable into textual descriptions.

## Quick Start (5 minutes)

1. **Install from repo:**
   ```bash
   cd /path/to/vibe_check
   pip install -e .
   pip install numpy pandas matplotlib  # Optional dependencies
   ```

2. **Configure OpenRouter API** (optional, for LLM mode):
   ```bash
   # Create .env file in repo root
   echo 'OPENROUTER_API_KEY=sk-or-v1-your-key' > .env
   ```

3. **Launch Jupyter:**
   ```bash
   jupyter notebook examples/quick_start.ipynb
   ```

4. **⚠️ IMPORTANT**: After installing, **restart your Jupyter kernel** before importing!

## What Was Created

### 📓 Jupyter Notebooks

#### `examples/quick_start.ipynb`
**Best for:** Getting started quickly (5-10 minutes)

- Installation and setup
- Basic usage with both modes
- Dictionary, List, NumPy, Pandas, Matplotlib examples
- Short and focused

#### `examples/notebook_demo.ipynb`
**Best for:** Learning all features (20-30 minutes)

- Comprehensive demonstrations
- 10 sections covering all capabilities
- Real-world workflow examples
- Detailed mode comparisons
- Code history tracking examples

### 🐍 Python Scripts

#### `examples/complete_demo.py`
**Best for:** Running without Jupyter

```bash
python examples/complete_demo.py
```

- Standalone demonstration
- All object types (built-ins, numpy, pandas, matplotlib)
- Both deterministic and LLM modes
- Works in any Python environment

#### `examples/verify_installation.py`
**Best for:** Testing your setup

```bash
python examples/verify_installation.py
```

- Checks installation
- Lists available adapters
- Tests basic functionality
- Verifies API configuration

### 📚 Documentation

#### `examples/README.md`
- Detailed examples guide
- Troubleshooting section
- Feature comparison table
- Installation help

## The Two Modes

### Deterministic Mode (`explain=False`)

**No API key required** - Instant, structured summaries

```python
import vibe_check as vibe
import pandas as pd

df = pd.DataFrame({'a': [1, 2, 3], 'b': [4, 5, 6]})

result = vibe.check(df, explain=False)
print(result.content)
# Output: pandas.DataFrame | Shape: (3, 2) | Columns: a, b | Types: a:int64, b:int64 | [via PandasAdapter]
```

**When to use:**
- ✅ Quick debugging and inspection
- ✅ When you don't have an API key
- ✅ Need instant results
- ✅ CI/CD pipelines or automated tests

### LLM Mode (`explain=True`)

**Requires OpenRouter API key** - Natural language explanations

```python
result = vibe.check(df, explain=True)
print(result.content)
# Output: "This DataFrame contains 3 rows and 2 columns (a and b), both with integer values.
#          The data shows a simple tabular structure with sequential values..."
```

**When to use:**
- ✅ Generating documentation
- ✅ Providing context to other LLMs
- ✅ Need semantic understanding
- ✅ Code history/provenance matters

## Object Types Demonstrated

All examples demonstrate these object types:

### 1. Built-in Types
```python
# Dictionary
data = {'name': 'Alice', 'age': 30}
vibe.check(data, explain=False)

# List
numbers = [1, 2, 3, 4, 5]
vibe.check(numbers, explain=False)

# Custom classes
class MyClass:
    def __init__(self):
        self.value = 42

obj = MyClass()
vibe.check(obj, explain=False)
```

### 2. NumPy Arrays
```python
import numpy as np

arr = np.random.randn(100, 5)

# Deterministic mode
result = vibe.check(arr, explain=False)

# LLM mode (with API key)
result = vibe.check(arr, explain=True)
```

### 3. Pandas DataFrames
```python
import pandas as pd

df = pd.DataFrame({
    'product': ['A', 'B', 'C'],
    'sales': [100, 200, 300]
})

# Get structured summary
result = vibe.check(df, explain=False)
print(result.meta['shape'])      # (3, 2)
print(result.meta['columns'])    # ['product', 'sales']
print(result.meta['dtypes'])     # {'product': 'object', 'sales': 'int64'}
```

### 4. Matplotlib Figures
```python
import matplotlib.pyplot as plt

fig, ax = plt.subplots()
ax.plot([1, 2, 3], [1, 4, 9])
ax.set_title('Quadratic Growth')

# The LLM uses code history to understand the plot!
result = vibe.check(fig, explain=True)
```

## Configuration Options

### Option 1: Environment Variable
```bash
export OPENROUTER_API_KEY="sk-or-v1-your-key"
```

### Option 2: `.env` File (Recommended)
```bash
# Create .env in repo root
OPENROUTER_API_KEY=sk-or-v1-your-key
VIBECHECK_MODEL=anthropic/claude-3.5-sonnet  # Optional
VIBECHECK_MAX_HISTORY=10                     # Optional
```

### Option 3: Programmatic
```python
import vibe_check as vibe

vibe.configure(
    openrouter_api_key="sk-or-v1-your-key",
    model="anthropic/claude-3.5-sonnet",
    max_history_lines=10
)
```

## Key Features Demonstrated

### 1. Installation from Local Repo
```python
# In notebook cells
!pip install -e ..
!pip install numpy pandas matplotlib

# Then RESTART KERNEL before continuing!
```

### 2. OpenRouter Configuration
```python
import os
from dotenv import load_dotenv
import vibe_check as vibe

load_dotenv('../.env')
api_key = os.getenv('OPENROUTER_API_KEY')

if api_key:
    vibe.configure(openrouter_api_key=api_key)
```

### 3. Multiple Object Types
- Built-ins: dict, list, custom classes
- NumPy: arrays
- Pandas: DataFrame, Series
- Matplotlib: Figure, Axes

### 4. Result Structure
```python
result = vibe.check(obj)

# Three key attributes
result.content   # Natural language summary (str)
result.meta      # Structured metadata (dict)
result.history   # Code history from Jupyter (list[str] | None)
```

### 5. Deterministic Mode (No API)
```python
# Fast summaries without API calls
result = vibe.check(obj, explain=False)
```

## Complete Workflow Example

```python
import vibe_check as vibe
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# 1. Configure (one time)
vibe.configure(openrouter_api_key="your-key")

# 2. Load data
df = pd.DataFrame({
    'date': pd.date_range('2024-01-01', periods=100, freq='D'),
    'sales': np.random.randint(100, 1000, 100)
})

# 3. Quick inspection (deterministic)
print(vibe.check(df, explain=False).content)

# 4. Transform data
monthly = df.groupby(df['date'].dt.month)['sales'].sum()

# 5. Create visualization
fig, ax = plt.subplots()
monthly.plot(kind='bar', ax=ax)
ax.set_title('Monthly Sales')

# 6. Generate report (LLM mode)
print("Data:", vibe.check(df, explain=True).content)
print("Summary:", vibe.check(monthly, explain=True).content)
print("Chart:", vibe.check(fig, explain=True).content)
```

## Troubleshooting

### `ModuleNotFoundError: No module named 'vibe_check'`

**Solution:** Restart your Jupyter kernel after installation!

1. Run installation cell: `!pip install -e ..`
2. **Kernel → Restart** (or click Restart button)
3. Continue from import cell

### `ConfigurationError: OpenRouter API key not configured`

Only happens with `explain=True` mode.

**Solution:** Set your API key (see Configuration Options above)

**Alternative:** Use `explain=False` mode (works without API key)

### Import errors for optional libraries

```bash
# Install individual libraries
pip install pandas numpy matplotlib

# Or install everything
pip install -e ".[all]"
```

## Bug Fix Applied

**Issue:** Specialized adapters weren't being used (all objects used GenericAdapter)

**Fix:** Modified `src/vibe_check/adapters/__init__.py` to import GenericAdapter last, ensuring specialized adapters are checked first.

**Result:** Now correctly uses:
- PandasAdapter for DataFrames
- MatplotlibAdapter for Figures
- SklearnAdapter for ML models
- etc.

## File Summary

```
examples/
├── README.md                    # Examples directory guide
├── quick_start.ipynb           # 5-minute intro notebook ⭐
├── notebook_demo.ipynb         # Complete feature demo ⭐
├── complete_demo.py            # Standalone Python script
├── verify_installation.py      # Setup verification tool
├── basic_demo.py              # Simple built-in types demo
└── pandas_demo.py             # Pandas-focused demo
```

## Next Steps

1. ✅ **Start here:** `examples/quick_start.ipynb`
2. ✅ **Learn more:** `examples/notebook_demo.ipynb`
3. ✅ **Test setup:** `python examples/verify_installation.py`
4. ✅ **Read docs:** Main [README.md](README.md)

---

**All examples are production-ready and run end-to-end in Jupyter notebooks! 🎉**
