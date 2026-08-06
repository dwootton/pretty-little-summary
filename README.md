# Pretty Little Summary

Automatic structured summaries of Python objects — DataFrames, arrays, models, plots, and more.

## Install

```bash
pip install pretty-little-summary
```

Optional adapters are enabled automatically when their libraries are installed.

No install? Try it in the browser: **[live playground](https://dwootton.github.io/pretty-little-summary/playground.html)** (runs via Pyodide, nothing uploaded).

## Features

- Single function API: `pls.describe(obj)`
- 40+ adapters across data, viz, and ML libraries
- Works with built-ins out of the box (no required deps)
- Jupyter/IPython history capture for better context

## Quick Start

```python
import pretty_little_summary as pls
import pandas as pd

df = pd.DataFrame({
    "product": ["Widget", "Gadget", "Doohickey"],
    "price": [19.99, 29.99, 39.99],
    "quantity": [100, 50, 75]
})

result = pls.describe(df)
print(result.content)
print(result.meta)
```

## Built-in Types

```python
import pretty_little_summary as pls

print(pls.describe([1, 2, 3]).content)
print(pls.describe({"name": "Alice", "age": 30}).content)
```

## NumPy Arrays

```python
import numpy as np
import pretty_little_summary as pls

arr = np.random.rand(100, 50)
result = pls.describe(arr)
print(result.content)
```

## Pandas DataFrames

```python
import pandas as pd
import pretty_little_summary as pls

df = pd.read_csv("data.csv")
result = pls.describe(df)
print(result.content)
```

## Matplotlib Figures

```python
import matplotlib.pyplot as plt
import pretty_little_summary as pls

fig, ax = plt.subplots()
ax.plot([1, 2, 3], [4, 5, 6])
result = pls.describe(fig)
print(result.content)
```

## History Tracking (Jupyter/IPython)

When running inside Jupyter, `pretty_little_summary` can capture recent code history that created your object:

```python
import pandas as pd
import pretty_little_summary as pls

df = pd.read_csv("data.csv")
df_clean = df.dropna()
result = pls.describe(df_clean)
print(result.history)
```

## Docs site

The docs (`docs/index.html`, `docs/playground.html`, `docs/eval-report.html`)
are a static site with no build step. To run it locally:

```bash
cd docs && python3 -m http.server 8000
```

Then open http://localhost:8000. Notes:

- `playground.html` loads [Pyodide](https://pyodide.org) from a CDN, so it
  needs internet access even when served locally.
- `playground.html` installs `pretty-little-summary` from `docs/dist/*.whl`
  so it always matches this commit's `src/` instead of a possibly-stale PyPI
  release. That wheel isn't committed — CI builds it on every docs deploy via
  `python -m build --wheel -o docs/dist`. Build it yourself before serving
  locally, or the playground falls back to installing from PyPI:
  ```bash
  .venv/bin/python -m build --wheel -o docs/dist
  ```
- `eval-report.html` isn't committed — generate it first with:
  ```bash
  .venv/bin/python -m evals.runner fetch
  .venv/bin/python -m evals.runner run
  .venv/bin/python -m evals.viewer --out docs/eval-report.html
  ```
  (CI does this automatically on every docs deploy.) Its markup lives in the
  committed `docs/eval-report-template.html`; `evals/viewer.py` only injects
  run data into it.
- The playground's curated/gallery example code comes from
  `docs/examples/*.txt`, regenerated via:
  ```bash
  .venv/bin/python scripts/export_examples.py
  ```

## Troubleshooting

### `ModuleNotFoundError: No module named 'pretty_little_summary'`

- Ensure you installed the package in the current environment.
- Restart your kernel or interpreter.

### Missing optional libraries

If an adapter isn’t available, install its library:

```bash
pip install pandas numpy matplotlib
```

Or install all optional dependencies:

```bash
pip install pretty-little-summary[all]
```
