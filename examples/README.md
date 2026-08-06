# Pretty Little Summary Examples

Runnable scripts demonstrating `pretty_little_summary`. For install steps,
API basics, and troubleshooting, see the main [README](../README.md).

## Scripts

- **`complete_demo.py`** — built-ins, NumPy, Pandas, and Matplotlib in one run
  ```bash
  python examples/complete_demo.py
  ```
- **`basic_demo.py`** — built-in types only (dict, list, custom classes)
  ```bash
  python examples/basic_demo.py
  ```
- **`pandas_demo.py`** — DataFrame summaries (requires pandas)
  ```bash
  pip install pandas
  python examples/pandas_demo.py
  ```
- **`showcase.py`** — broader tour across adapters
- **`verify_installation.py`** — checks install and lists available optional adapters
  ```bash
  python examples/verify_installation.py
  ```

## Notes

- History tracking (`result.history`) only works in IPython/Jupyter.
- Optional adapters activate automatically when their libraries are installed.
