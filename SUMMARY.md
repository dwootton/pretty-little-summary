# Optional Dependencies Implementation Summary

## What Was Done

Your `wut-is` library is **already correctly set up** for optional dependencies! Here's what was reviewed and enhanced:

### 1. **Existing Implementation** ✓

Your library already had the correct pattern:

- **Minimal core dependencies** (src/wut_is/adapters/_base.py:24):
  - Only `httpx` and `python-dotenv` are required
  - All data science libraries are optional

- **Lazy imports in adapters** (e.g., src/wut_is/adapters/pandas.py:6-9):
  ```python
  try:
      import pandas as pd
      LIBRARY_AVAILABLE = True
  except ImportError:
      LIBRARY_AVAILABLE = False
  ```

- **Runtime availability checks** (src/wut_is/adapters/pandas.py:22-23):
  ```python
  def can_handle(obj):
      if not LIBRARY_AVAILABLE:
          return False
  ```

- **Safe adapter loading** (src/wut_is/adapters/__init__.py:10-38):
  ```python
  try:
      from wut_is.adapters.pandas import PandasAdapter
  except ImportError:
      pass  # Silently skip if pandas not installed
  ```

### 2. **New Features Added**

#### A. `list_available_adapters()` Function
- **Location**: src/wut_is/adapters/_base.py:65-80
- **Purpose**: Lets users see which adapters are active based on installed libraries
- **Usage**:
  ```python
  import wut_is as wut
  print(wut.list_available_adapters())
  # ['PandasAdapter', 'MatplotlibAdapter', 'NumpyAdapter', ...]
  ```

#### B. Comprehensive Tests
- **test_list_adapters.py** (tests/test_list_adapters.py:1): Tests for the new utility function
- **test_minimal_install.py** (tests/test_minimal_install.py:1): Ensures core functionality works without optional dependencies

#### C. Documentation
- **OPTIONAL_DEPENDENCIES.md** (OPTIONAL_DEPENDENCIES.md:1): Complete guide for users
- **demo_optional_deps.py** (demo_optional_deps.py:1): Interactive demonstration

## How It Works for End Users

### Installation Patterns

**Pattern 1: Minimal (Recommended)**
```bash
# User already has their stack
pip install pandas numpy matplotlib

# Just add wut-is
pip install wut-is

# Works automatically!
import wut_is as wut
wut.is_(my_dataframe)  # PandasAdapter auto-activates
```

**Pattern 2: With Extras**
```bash
pip install wut-is[pandas,viz]  # Install specific extras
```

**Pattern 3: Everything**
```bash
pip install wut-is[all]  # For development
```

### Runtime Behavior

1. **Import Time**:
   - Each adapter tries to import its library
   - Sets `LIBRARY_AVAILABLE = True/False`
   - Only registers if library is available

2. **Usage Time**:
   - `wut.is_(obj)` calls each adapter's `can_handle(obj)`
   - Adapters with unavailable libraries return `False` immediately
   - Falls back to `GenericAdapter` if no adapter matches

3. **No Errors**:
   - Missing libraries don't break anything
   - Users only get adapters for what they have installed

## Package Structure

```
pyproject.toml
├── [project.dependencies]
│   ├── httpx>=0.27.0          # Core (always installed)
│   └── python-dotenv>=1.0.0   # Core (always installed)
│
└── [project.optional-dependencies]
    ├── pandas = ["pandas>=2.0.0"]
    ├── polars = ["polars>=0.20.0"]
    ├── matplotlib = ["matplotlib>=3.8.0"]
    ├── data = ["pandas>=2.0.0", "polars>=0.20.0"]
    ├── viz = ["matplotlib>=3.8.0", "altair>=5.0.0"]
    ├── ml = ["scikit-learn>=1.4.0", "torch>=2.0.0"]
    └── all = [...]  # Everything (for dev/testing)
```

## Adapter Registration Flow

```
User runs: import wut_is

1. wut_is/__init__.py loads
2. wut_is/adapters/__init__.py loads
3. For each adapter:
   a. Try to import adapter module
   b. Adapter module tries to import its library
   c. If library available:
      - Set LIBRARY_AVAILABLE = True
      - Register adapter with AdapterRegistry
   d. If library unavailable:
      - Set LIBRARY_AVAILABLE = False
      - Skip registration (or return False from can_handle)
4. GenericAdapter always loads (fallback)

User calls: wut.is_(obj)

1. dispatch_adapter(obj) is called
2. AdapterRegistry checks each registered adapter
3. First adapter where can_handle(obj) == True wins
4. That adapter's extract_metadata(obj) is called
5. If no adapter matches, GenericAdapter is used
```

## Testing the Pattern

### Run Tests
```bash
# Test the list_available_adapters function
pytest tests/test_list_adapters.py -v

# Test minimal install functionality
pytest tests/test_minimal_install.py -v

# Run all tests
pytest -v
```

### Run Demo
```bash
python demo_optional_deps.py
```

This shows:
- What adapters are available initially
- How adapters activate when libraries are imported
- How it works with/without optional dependencies

## Key Advantages

1. **Lightweight**: Core install is ~2 dependencies vs. ~15+ if all were required
2. **User-Friendly**: Works with existing installations automatically
3. **No Breaking Changes**: Missing libraries don't cause import errors
4. **Gradual Adoption**: Users can add libraries incrementally
5. **Developer-Friendly**: Easy to test with/without specific libraries

## For Publishing

When you publish to PyPI:

```bash
# Build the package
python -m build

# Users install minimal version
pip install wut-is

# Or with extras
pip install wut-is[data,viz]
```

The `pyproject.toml` already has everything configured correctly!

## Common User Scenarios

### Scenario 1: Data Scientist with Existing Stack
```bash
# Already has pandas, numpy, matplotlib
pip install wut-is
# Works immediately with all their types!
```

### Scenario 2: New User, Specific Need
```bash
pip install wut-is[pandas]
# Gets pandas + wut-is, nothing extra
```

### Scenario 3: Library Developer
```bash
pip install wut-is
# Minimal dependencies, no bloat in their project
```

### Scenario 4: Comprehensive Testing
```bash
pip install wut-is[all]
# Everything for testing/development
```

## Files Modified/Created

### Modified
- `src/wut_is/adapters/_base.py` - Added `list_available_adapters()`
- `src/wut_is/adapters/__init__.py` - Export new function
- `src/wut_is/__init__.py` - Export new function at top level

### Created
- `tests/test_list_adapters.py` - Tests for the utility function
- `tests/test_minimal_install.py` - Tests for minimal install scenario
- `demo_optional_deps.py` - Interactive demonstration
- `OPTIONAL_DEPENDENCIES.md` - User documentation
- `SUMMARY.md` - This file

## Next Steps

1. ✓ Your package structure is already correct
2. ✓ Tests verify it works
3. ✓ Documentation explains it

**You're ready to publish!** Your library will work great for users whether they:
- Have a full data science stack installed
- Only have specific libraries
- Just want the core functionality

The pattern is production-ready and follows Python best practices for optional dependencies.
