"""Pandas demonstration of pretty_little_summary functionality.

Run with: uv pip install pandas && python examples/pandas_demo.py
"""

try:
    import pandas as pd
except ImportError:
    print("This example requires pandas.")
    print("Install with: uv pip install pandas")
    exit(1)

import pretty_little_summary as pls

# Create sample DataFrame
df = pd.DataFrame({
    'name': ['Alice', 'Bob', 'Charlie', 'David', 'Eve'],
    'age': [25, 30, 35, 40, 45],
    'salary': [50000, 60000, 70000, 80000, 90000],
    'department': ['Engineering', 'Sales', 'Engineering', 'HR', 'Sales']
})

print("=" * 70)
print("Pandas DataFrame Example")
print("=" * 70)

print("\nDataFrame:")
print(df)

# Check with deterministic summary
result = pls.describe(df)

print("\n" + "=" * 70)
print("PLS Result")
print("=" * 70)

print(f"\nContent:\n{result.content}")

print(f"\nDetailed Metadata:")
print(f"  Object Type: {result.meta['object_type']}")
print(f"  Adapter Used: {result.meta['adapter_used']}")
print(f"  Shape: {result.meta['shape']}")
print(f"  Columns: {result.meta['columns']}")
print(f"\n  Data Types:")
for col, dtype in result.meta['dtypes'].items():
    print(f"    {col}: {dtype}")

if 'sample_data' in result.meta:
    print(f"\n  Sample Data:")
    print(result.meta['sample_data'])

print("\n" + "=" * 70)
print("Success! PandasAdapter works correctly.")
print("=" * 70)
