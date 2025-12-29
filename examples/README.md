# Wut Is Examples

This directory contains comprehensive examples demonstrating how to use wut_is.

## Quick Start

1. **Install wut_is** (from the repo root):
   ```bash
   cd /path/to/wut_is
   pip install -e .
   ```

2. **Install optional dependencies**:
   ```bash
   pip install numpy pandas matplotlib
   ```

3. **Set up your API key** (optional, for LLM mode):

   Create a `.env` file in the project root:
   ```bash
   OPENROUTER_API_KEY=sk-or-v1-your-key-here
   ```

## Available Examples

### 📓 Jupyter Notebooks (Recommended)

#### `quick_start.ipynb` - Start here!
- Fast 5-minute introduction
- Basic usage of both modes (deterministic & LLM)
- Works with dict, pandas, numpy, matplotlib
- **Best for**: Getting started quickly

#### `notebook_demo.ipynb` - Complete guide
- Comprehensive demonstration of all features
- Detailed explanations and comparisons
- Real-world workflow examples
- **Best for**: Learning all capabilities

### 🐍 Python Scripts

#### `complete_demo.py` - Standalone demo
- Run directly from command line
- No Jupyter required
- All features demonstrated
- Usage:
  ```bash
  python examples/complete_demo.py
  ```

#### `basic_demo.py` - Simple examples
- Built-in types (dict, list, custom classes)
- Deterministic mode only
- Usage:
  ```bash
  python examples/basic_demo.py
  ```

#### `pandas_demo.py` - Pandas-specific
- Focuses on DataFrame analysis
- Requires pandas
- Usage:
  ```bash
  pip install pandas
  python examples/pandas_demo.py
  ```

## Running the Notebooks

### Option 1: Jupyter Notebook
```bash
jupyter notebook examples/
```

### Option 2: JupyterLab
```bash
jupyter lab examples/
```

### Option 3: VS Code
1. Open the `.ipynb` file in VS Code
2. Select a Python kernel
3. Run cells

## Important: Kernel Restart

**⚠️ After installing wut_is, you MUST restart your Jupyter kernel!**

Otherwise, you'll get `ModuleNotFoundError: No module named 'wut_is'`

### How to restart:
- **Jupyter Notebook**: Kernel → Restart
- **JupyterLab**: Kernel → Restart Kernel
- **VS Code**: Click "Restart" in the notebook toolbar

## Two Modes Explained

### Deterministic Mode (`explain=False`)
```python
result = wut.is_(df, explain=False)
```
- ✅ No API key required
- ✅ Instant results
- ✅ Structured, predictable output
- ✅ Perfect for quick inspection

**Output example:**
```
pandas.DataFrame | Shape: (100, 5) | Columns: date, product, quantity, price, region | [via PandasAdapter]
```

### LLM Mode (`explain=True`)
```python
result = wut.is_(df, explain=True)
```
- ✅ Requires OpenRouter API key
- ✅ Natural language explanation
- ✅ Uses code history for context
- ✅ Perfect for documentation/LLM consumption

**Output example:**
```
This DataFrame contains 100 rows of sales data spanning from January to April 2024.
It tracks transactions across 5 columns including dates, product types (Widget A, B, C),
quantities, prices, and regions. A calculated revenue column shows the total value of
each transaction.
```

## What Each Example Demonstrates

| Example | Built-ins | NumPy | Pandas | Matplotlib | Deterministic | LLM | History |
|---------|-----------|-------|--------|------------|---------------|-----|---------|
| `quick_start.ipynb` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `notebook_demo.ipynb` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `complete_demo.py` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| `basic_demo.py` | ✅ | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ |
| `pandas_demo.py` | ❌ | ❌ | ✅ | ❌ | ✅ | ❌ | ❌ |

**Note**: History tracking only works in Jupyter/IPython environments

## Troubleshooting

### `ModuleNotFoundError: No module named 'wut_is'`

**Solution**: Restart your Jupyter kernel after installation!

1. Make sure you installed: `pip install -e .` (from repo root)
2. **Restart the kernel**: Kernel → Restart
3. Try importing again: `import wut_is as wut`

### `ConfigurationError: OpenRouter API key not configured`

This error only appears when using `explain=True` mode.

**Solution**: Set your API key

Option A - Environment variable:
```bash
export OPENROUTER_API_KEY="sk-or-v1-your-key"
```

Option B - `.env` file (recommended):
```bash
echo 'OPENROUTER_API_KEY=sk-or-v1-your-key' > .env
```

Option C - Programmatic:
```python
vibe.configure(openrouter_api_key="sk-or-v1-your-key")
```

**Note**: Deterministic mode (`explain=False`) works without an API key!

### Import errors for optional libraries

If you see errors like `ModuleNotFoundError: No module named 'pandas'`:

```bash
# Install individual libraries
pip install pandas numpy matplotlib

# Or install all at once
pip install -e ".[all]"
```

## Next Steps

1. ✅ Start with `quick_start.ipynb` to learn the basics
2. ✅ Explore `notebook_demo.ipynb` for comprehensive examples
3. ✅ Read the main [README.md](../README.md) for full documentation
4. ✅ Check [src/wut_is/adapters/](../src/wut_is/adapters/) to see all supported libraries

## Getting Help

- **Documentation**: See main [README.md](../README.md)
- **Issues**: Report bugs or request features on GitHub
- **API Reference**: Check docstrings in the source code

---

**Happy vibing! 🎉**
