# Changelog

## v0.1.0 - Complete Rename & Enhancement

### Breaking Changes

**Package Rename**: `vibe_check` → `pretty_little_summary`
- Package name: `pip install pretty-little-summary` (was `vibe-check`)
- Import: `import pretty_little_summary as pls` (was `import vibe_check as vibe`)
- Main function: `pls.describe(obj)` (was `vibe.check(obj)`)
- Result class: `Description` (was `VibeCheck`)

### Major Improvements

#### 1. Enhanced Deterministic Output for Built-in Types

**Before**:
```
builtins.dict | [via GenericAdapter]
builtins.list | [via GenericAdapter]
```

**After**:
```
builtins.dict | Length: 3 | Keys: name, age, city | Sample: {name: str, age: int, city: str} | [via GenericAdapter]
builtins.list | Length: 10 | Element types: int | [via GenericAdapter]
builtins.str | Length: 55 | "This is a sample text..." | [via GenericAdapter]
```

#### 2. Improved GenericAdapter

Now extracts useful metadata for:
- **Dictionaries**: length, keys, sample items with types
- **Lists/Tuples**: length, element types, sample items
- **Sets**: length, element types
- **Strings**: length, preview
- **Numbers**: values
- **Custom classes**: attributes

#### 3. Better Adapter Dispatch

Fixed issue where GenericAdapter was matching before specialized adapters. Now correctly uses:
- PandasAdapter for DataFrames
- MatplotlibAdapter for Figures
- All 10+ specialized adapters

### Migration Guide

#### Update Imports
```python
# Old
import vibe_check as vibe
vibe.configure(...)
result = vibe.check(df)

# New
import pretty_little_summary as pls
pls.configure(...)
result = pls.describe(df)
```

#### Update Configuration
```bash
# Old
export VIBECHECK_MODEL=...
VIBECHECK_MAX_HISTORY=...

# New
export WUTIS_MODEL=...
WUTIS_MAX_HISTORY=...
```

#### Update Code
```python
# Old
from vibe_check import VibeCheck, check, configure

# New
from pretty_little_summary import Description, is_, configure
```

### Installation

```bash
# Uninstall old package
pip uninstall vibe-check

# Install new package
pip install -e .
```

### Examples Updated

All examples have been updated:
- ✅ `examples/quick_start.ipynb`
- ✅ `examples/notebook_demo.ipynb`
- ✅ `examples/complete_demo.py`
- ✅ `examples/basic_demo.py`
- ✅ `examples/pandas_demo.py`
- ✅ `examples/verify_installation.py`

### Output Examples

```python
import pretty_little_summary as pls

# Dictionary - now shows structure!
data = {'name': 'Alice', 'age': 30}
pls.describe(data, explain=False)
# Output: builtins.dict | Length: 2 | Keys: name, age | Sample: {name: str, age: int} | [via GenericAdapter]

# List - shows elements!
numbers = [1, 2, 3, 4, 5]
pls.describe(numbers, explain=False)
# Output: builtins.list | Length: 5 | Element types: int | [via GenericAdapter]

# DataFrame - clean and structured!
df = pd.DataFrame({'a': [1, 2], 'b': [3, 4]})
pls.describe(df, explain=False)
# Output: pandas.DataFrame | Shape: (2, 2) | Columns: a, b | Types: a:int64, b:int64 | [via PandasAdapter]
```

### What Stayed the Same

- Same LLM integration via OpenRouter
- Same adapter system architecture
- Same two modes: `explain=True` (LLM) and `explain=False` (deterministic)
- Same support for 10+ libraries
- Same history tracking in Jupyter

---

**Note**: The package name changed but the core functionality is enhanced and improved!
