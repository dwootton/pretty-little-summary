"""
Pretty Little Summary - Complete Demo

This script demonstrates pretty_little_summary with various object types.
Can be run directly or copied into a Jupyter notebook.

Installation:
    pip install -e .
    pip install numpy pandas matplotlib
"""

import sys

# Import pretty_little_summary
try:
    import pretty_little_summary as pls
except ImportError:
    print("ERROR: pretty_little_summary not installed.")
    print("Install with: pip install -e .")
    sys.exit(1)


def print_section(title):
    """Print a formatted section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_result(result):
    """Print a pls result nicely."""
    print(f"\nContent: {result.content}")

    if result.meta:
        print("\nKey Metadata:")
        for key in ["object_type", "adapter_used", "shape", "columns"]:
            if key in result.meta:
                print(f"  {key}: {result.meta[key]}")

    if result.history:
        print(f"\nHistory (last 3 lines): {result.history[-3:]}")


def demo_1_builtin_types():
    """Demo with built-in Python types."""
    print_section("1. Built-in Types")

    # Dictionary
    print("\n📦 Dictionary:")
    user_data = {
        "name": "Alice Johnson",
        "age": 28,
        "email": "alice@example.com",
        "roles": ["admin", "developer"],
        "active": True,
    }
    result = pls.describe(user_data)
    print_result(result)

    # List
    print("\n📦 List:")
    numbers = list(range(1, 101))
    result = pls.describe(numbers)
    print_result(result)

    # Custom class
    print("\n📦 Custom Class:")
    class DataPipeline:
        def __init__(self, name, steps):
            self.name = name
            self.steps = steps
            self.executed = False

    pipeline = DataPipeline("ETL_Pipeline", ["extract", "transform", "load"])
    result = pls.describe(pipeline)
    print_result(result)


def demo_2_numpy():
    """Demo with NumPy arrays."""
    print_section("2. NumPy Arrays")

    try:
        import numpy as np
    except ImportError:
        print("⚠ NumPy not installed. Install with: pip install numpy")
        return

    # Create a 2D array
    arr = np.random.randn(100, 5)

    print("\n🔢 NumPy Array (100x5 random values):")
    result = pls.describe(arr)
    print_result(result)


def demo_3_pandas():
    """Demo with Pandas DataFrames."""
    print_section("3. Pandas DataFrames")

    try:
        import pandas as pd
        import numpy as np
    except ImportError:
        print("⚠ Pandas not installed. Install with: pip install pandas")
        return

    # Create sample sales data
    df = pd.DataFrame(
        {
            "date": pd.date_range("2024-01-01", periods=100, freq="D"),
            "product": np.random.choice(["Widget A", "Widget B", "Widget C"], 100),
            "quantity": np.random.randint(1, 50, 100),
            "price": np.random.uniform(10, 100, 100).round(2),
            "region": np.random.choice(["North", "South", "East", "West"], 100),
        }
    )
    df["revenue"] = df["quantity"] * df["price"]

    print("\n📊 Sales DataFrame (100 rows, 6 columns):")
    print(df.head(3))

    result = pls.describe(df)
    print_result(result)

    # Aggregated data
    print("\n\n📊 Aggregated Data:")
    summary = df.groupby("product")["revenue"].agg(["sum", "mean", "count"])
    print(summary)

    result = pls.describe(summary)
    print_result(result)


def demo_4_matplotlib():
    """Demo with Matplotlib figures."""
    print_section("4. Matplotlib Figures")

    try:
        import matplotlib

        matplotlib.use("Agg")  # Non-interactive backend
        import matplotlib.pyplot as plt
        import numpy as np
    except ImportError:
        print("⚠ Matplotlib not installed. Install with: pip install matplotlib")
        return

    # Create a figure with subplots
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))

    # Plot 1: Line plot
    x = np.linspace(0, 10, 100)
    axes[0].plot(x, np.sin(x), label="sin(x)")
    axes[0].plot(x, np.cos(x), label="cos(x)")
    axes[0].set_title("Trigonometric Functions")
    axes[0].set_xlabel("X")
    axes[0].set_ylabel("Y")
    axes[0].legend()
    axes[0].grid(True)

    # Plot 2: Scatter plot
    x = np.random.randn(100)
    y = 2 * x + np.random.randn(100) * 0.5
    axes[1].scatter(x, y, alpha=0.5)
    axes[1].set_title("Linear Relationship")
    axes[1].set_xlabel("X")
    axes[1].set_ylabel("Y")

    plt.tight_layout()

    print("\n📈 Matplotlib Figure (2 subplots created):")
    result = pls.describe(fig)
    print_result(result)

    plt.close(fig)


def main():
    """Run all demos."""
    print("=" * 70)
    print("  Pretty Little Summary - Complete Demo")
    print("  Structured Summaries of Python Objects")
    print("=" * 70)

    # Run demos
    try:
        demo_1_builtin_types()
        demo_2_numpy()
        demo_3_pandas()
        demo_4_matplotlib()
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user")
        return
    except Exception as e:
        print(f"\n\nError during demo: {e}")
        import traceback

        traceback.print_exc()
        return

    # Summary
    print_section("Summary")
    print("\n✅ Demo completed successfully!")
    print("\nKey Points:")
    print("  1. Install: pip install -e .")
    print("  2. Use: pls.describe(obj)")
    print("\nSupported Types:")
    print("  • Built-ins: dict, list, custom classes")
    print("  • NumPy: arrays, matrices")
    print("  • Pandas: DataFrame, Series")
    print("  • Matplotlib: Figure, Axes")
    print("  • And many more adapters")
    print("\nNext Steps:")
    print("  • Read the docs: README.md")
    print("  • Explore adapters: src/pretty_little_summary/adapters/")
    print()


if __name__ == "__main__":
    main()
