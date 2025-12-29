# Pretty Little Summary

Automatic structured summaries of Python objects — DataFrames, arrays, models, plots, and more.

## Install

```bash
pip install pretty-little-summary
```

Optional adapters are enabled automatically when their libraries are installed.

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
