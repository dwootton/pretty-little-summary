# Pretty Little Summary Examples

This directory contains runnable examples for pretty_little_summary.

## Quick Start

1. Install pretty_little_summary (from repo root):
   ```bash
   cd /path/to/pretty_little_summary
   pip install -e .
   ```

2. Install optional dependencies as needed:
   ```bash
   pip install numpy pandas matplotlib
   ```

## Available Examples

### `complete_demo.py` - Standalone demo
- Run directly from command line
- Demonstrates built-ins, NumPy, Pandas, and Matplotlib
- Usage:
  ```bash
  python examples/complete_demo.py
  ```

### `basic_demo.py` - Simple examples
- Built-in types (dict, list, custom classes)
- Usage:
  ```bash
  python examples/basic_demo.py
  ```

### `pandas_demo.py` - Pandas-specific
- Focuses on DataFrame summaries
- Requires pandas
- Usage:
  ```bash
  pip install pandas
  python examples/pandas_demo.py
  ```

### `verify_installation.py` - Environment check
- Verifies install and available optional adapters
- Usage:
  ```bash
  python examples/verify_installation.py
  ```

## Notes

- History tracking works in IPython/Jupyter environments.
- Optional adapters are auto-enabled when their libraries are installed.

## Troubleshooting

### `ModuleNotFoundError: No module named 'pretty_little_summary'`

1. Make sure you installed: `pip install -e .` (from repo root)
2. Restart your Python kernel/interpreter
3. Try importing again: `import pretty_little_summary as pls`

### Import errors for optional libraries

If you see errors like `ModuleNotFoundError: No module named 'pandas'`:

```bash
# Install individual libraries
pip install pandas numpy matplotlib

# Or install all at once
pip install -e ".[all]"
```

## Next Steps

1. Read the main README: `README.md`
2. Explore adapters: `src/pretty_little_summary/adapters/`
