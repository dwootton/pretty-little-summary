#!/usr/bin/env python3
"""
Pretty Little Summary - Showcase of Deterministic Output

This script demonstrates pretty_little_summary output for common Python objects.

Run: python examples/showcase.py
"""

import pretty_little_summary as pls


def section(title):
    """Print a section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def show(description, obj):
    """Show an object's pretty_little_summary output."""
    result = pls.describe(obj)
    print(f"\n{description}:")
    print(f"  {result.content}\n")


def main():
    """Run the showcase."""
    print("=" * 70)
    print("  Pretty Little Summary - Deterministic Showcase")
    print("  Structured Summaries Without Extra Dependencies")
    print("=" * 70)

    # Built-in Types
    section("Built-in Python Types")

    show(
        "Dictionary with mixed types",
        {
            'name': 'Alice Johnson',
            'age': 28,
            'active': True,
            'scores': [95, 87, 92, 88],
            'metadata': {'role': 'admin', 'department': 'Engineering'}
        }
    )

    show(
        "List of integers",
        list(range(1, 101))
    )

    show(
        "Mixed-type list",
        [1, "hello", 3.14, True, None, {"key": "value"}]
    )

    show(
        "Long string",
        "This is a sample string that demonstrates how pretty_little_summary handles text content. "
        "It will show the length and a preview of the content."
    )

    show(
        "Tuple of coordinates",
        (42.3601, -71.0589, 15.5)
    )

    show(
        "Set of values",
        {1, 2, 3, 4, 5, 6, 7, 8, 9, 10}
    )

    show(
        "Boolean value",
        True
    )

    show(
        "Integer",
        42
    )

    show(
        "Float",
        3.141592653589793
    )

    show(
        "None value",
        None
    )

    # NumPy (if available)
    section("NumPy Arrays")
    try:
        import numpy as np

        show(
            "2D NumPy array (100x5)",
            np.random.randn(100, 5)
        )

        show(
            "1D array of integers",
            np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        )

    except ImportError:
        print("\n⚠ NumPy not installed - skipping numpy examples")
        print("  Install with: pip install numpy")

    # Pandas (if available)
    section("Pandas DataFrames")
    try:
        import pandas as pd
        import numpy as np

        show(
            "Sales DataFrame",
            pd.DataFrame({
                'date': pd.date_range('2024-01-01', periods=50, freq='D'),
                'product': np.random.choice(['Widget A', 'Widget B', 'Widget C'], 50),
                'quantity': np.random.randint(1, 100, 50),
                'price': np.random.uniform(10, 500, 50).round(2),
                'region': np.random.choice(['North', 'South', 'East', 'West'], 50)
            })
        )

        show(
            "Aggregated data (grouped)",
            pd.DataFrame({
                'product': ['Widget A', 'Widget B', 'Widget C'] * 10,
                'sales': np.random.randint(100, 1000, 30)
            }).groupby('product')['sales'].sum()
        )

    except ImportError:
        print("\n⚠ Pandas not installed - skipping pandas examples")
        print("  Install with: pip install pandas")

    # Matplotlib (if available)
    section("Matplotlib Figures")
    try:
        import matplotlib
        matplotlib.use('Agg')  # Non-interactive backend
        import matplotlib.pyplot as plt
        import numpy as np

        fig, ax = plt.subplots()
        x = np.linspace(0, 10, 100)
        ax.plot(x, np.sin(x))
        ax.set_title('Sine Wave')

        show("Simple line plot", fig)

        plt.close(fig)

    except ImportError:
        print("\n⚠ Matplotlib not installed - skipping matplotlib examples")
        print("  Install with: pip install matplotlib")

    # Custom Classes
    section("Custom Classes")

    class User:
        def __init__(self, name, email):
            self.name = name
            self.email = email
            self.created_at = "2024-01-15"
            self.active = True

        def get_info(self):
            return f"{self.name} ({self.email})"

    show(
        "Custom User class",
        User("Alice Johnson", "alice@example.com")
    )

    class DataPipeline:
        def __init__(self):
            self.steps = ['extract', 'transform', 'load']
            self.status = 'ready'
            self.retries = 3
            self.timeout = 300

        def run(self):
            pass

        def validate(self):
            pass

    show(
        "Custom DataPipeline class",
        DataPipeline()
    )

    # Summary
    section("Summary")
    print("\n✅ All outputs show useful, structured information!")
    print("\nKey Features:")
    print("  • No API key required")
    print("  • Instant results")
    print("  • Structured, readable output")
    print("  • Works with built-ins, NumPy, Pandas, and custom classes")
    print()


if __name__ == "__main__":
    main()
