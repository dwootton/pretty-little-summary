"""
Demo script showing how optional dependencies work in wut-is.

This script demonstrates:
1. Core functionality works without any optional dependencies
2. Adapters automatically activate when libraries are imported
3. list_available_adapters() shows what's currently available
"""

import wut_is as wut

print("=" * 60)
print("WUT-IS OPTIONAL DEPENDENCIES DEMO")
print("=" * 60)
print()

# Show what's available initially
print("Initially available adapters:")
initial_adapters = wut.list_available_adapters()
for adapter in sorted(initial_adapters):
    print(f"  - {adapter}")
print(f"\nTotal: {len(initial_adapters)} adapters")
print()

# Test with a simple Python object (always works)
print("-" * 60)
print("Testing with built-in types (no optional deps needed):")
print("-" * 60)

my_list = [1, 2, 3, 4, 5]
result = wut.is_(my_list, explain=False)
print(f"\nObject: {my_list}")
print(f"Summary: {result.content}")
print()

my_dict = {"name": "Alice", "age": 30, "city": "NYC"}
result = wut.is_(my_dict, explain=False)
print(f"\nObject: {my_dict}")
print(f"Summary: {result.content}")
print()

# Try importing pandas (if available)
print("-" * 60)
print("Testing with pandas (if installed):")
print("-" * 60)

try:
    import pandas as pd

    print("\nPandas is installed! Creating a DataFrame...")
    df = pd.DataFrame(
        {"name": ["Alice", "Bob", "Charlie"], "age": [25, 30, 35], "score": [92.5, 88.0, 95.5]}
    )

    # Note: PandasAdapter should now be available
    adapters_after_pandas = wut.list_available_adapters()
    if "PandasAdapter" in adapters_after_pandas:
        print("✓ PandasAdapter is now active!")

    result = wut.is_(df, explain=False)
    print(f"\nDataFrame:")
    print(df)
    print(f"\nSummary: {result.content}")
    print()

except ImportError:
    print("\nPandas is not installed - skipping pandas example")
    print("Install with: pip install pandas")
    print()

# Try importing matplotlib (if available)
print("-" * 60)
print("Testing with matplotlib (if installed):")
print("-" * 60)

try:
    import matplotlib.pyplot as plt
    import numpy as np

    print("\nMatplotlib is installed! Creating a figure...")

    # Note: MatplotlibAdapter should now be available
    adapters_after_mpl = wut.list_available_adapters()
    if "MatplotlibAdapter" in adapters_after_mpl:
        print("✓ MatplotlibAdapter is now active!")

    fig, ax = plt.subplots()
    x = np.linspace(0, 10, 100)
    ax.plot(x, np.sin(x))
    ax.set_title("Sine Wave")
    ax.set_xlabel("X")
    ax.set_ylabel("Y")

    result = wut.is_(fig, explain=False)
    print(f"\nSummary: {result.content}")
    print()

except ImportError:
    print("\nMatplotlib is not installed - skipping matplotlib example")
    print("Install with: pip install matplotlib")
    print()

# Final adapter count
print("=" * 60)
print("FINAL ADAPTER COUNT")
print("=" * 60)
final_adapters = wut.list_available_adapters()
print(f"\nTotal adapters available: {len(final_adapters)}")
print("\nFull list:")
for adapter in sorted(final_adapters):
    print(f"  - {adapter}")
print()

print("=" * 60)
print("INSTALLATION GUIDE")
print("=" * 60)
print("""
To install wut-is with optional dependencies:

Basic installation (minimal dependencies):
  pip install wut-is

With specific libraries:
  pip install wut-is[pandas]       # Pandas support
  pip install wut-is[viz]          # Visualization (matplotlib + altair)
  pip install wut-is[ml]           # Machine learning (sklearn + pytorch)
  pip install wut-is[data,ml]      # Multiple groups

For development (all adapters):
  pip install wut-is[all]

Or just install wut-is and use your existing libraries:
  # If you already have pandas, numpy, etc. installed,
  # wut-is will automatically detect and use them!
  pip install wut-is
""")
