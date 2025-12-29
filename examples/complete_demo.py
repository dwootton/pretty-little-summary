"""
Complete Wut Is Demo - Notebook-Ready Examples

This script demonstrates all features of wut_is with various object types.
Can be run directly or copied into a Jupyter notebook.

Installation:
    pip install -e .
    pip install numpy pandas matplotlib

Configuration:
    export OPENROUTER_API_KEY="sk-or-v1-your-key"
    # OR set it in .env file
"""

import os
import sys
from dotenv import load_dotenv

# Import wut_is
try:
    import wut_is as wut
except ImportError:
    print("ERROR: wut_is not installed.")
    print("Install with: pip install -e .")
    sys.exit(1)

# Load configuration
load_dotenv()
api_key = os.getenv('OPENROUTER_API_KEY')


def print_section(title):
    """Print a formatted section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_result(result, mode="deterministic"):
    """Print a wut check result nicely."""
    print(f"\n{mode.upper()} MODE:")
    print(f"Content: {result.content}")

    if result.meta:
        print(f"\nKey Metadata:")
        for key in ['object_type', 'adapter_used', 'shape', 'columns']:
            if key in result.meta:
                print(f"  {key}: {result.meta[key]}")

    if result.history:
        print(f"\nHistory (last 3 lines): {result.history[-3:]}")


def demo_1_builtin_types():
    """Demo with built-in Python types."""
    print_section("1. Built-in Types (Deterministic Mode)")

    # Dictionary
    print("\n📦 Dictionary:")
    user_data = {
        'name': 'Alice Johnson',
        'age': 28,
        'email': 'alice@example.com',
        'roles': ['admin', 'developer'],
        'active': True
    }
    result = wut.is_(user_data, explain=False)
    print_result(result)

    # List
    print("\n📦 List:")
    numbers = list(range(1, 101))
    result = wut.is_(numbers, explain=False)
    print_result(result)

    # Custom class
    print("\n📦 Custom Class:")
    class DataPipeline:
        def __init__(self, name, steps):
            self.name = name
            self.steps = steps
            self.executed = False

    pipeline = DataPipeline("ETL_Pipeline", ["extract", "transform", "load"])
    result = wut.is_(pipeline, explain=False)
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
    result = wut.is_(arr, explain=False)
    print_result(result, "deterministic")

    # Try LLM mode if API key available
    if api_key:
        print("\nTrying LLM mode...")
        result = wut.is_(arr, explain=True)
        print_result(result, "llm")
    else:
        print("\n⚠ No API key - skipping LLM mode")


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
    df = pd.DataFrame({
        'date': pd.date_range('2024-01-01', periods=100, freq='D'),
        'product': np.random.choice(['Widget A', 'Widget B', 'Widget C'], 100),
        'quantity': np.random.randint(1, 50, 100),
        'price': np.random.uniform(10, 100, 100).round(2),
        'region': np.random.choice(['North', 'South', 'East', 'West'], 100)
    })
    df['revenue'] = df['quantity'] * df['price']

    print("\n📊 Sales DataFrame (100 rows, 6 columns):")
    print(df.head(3))

    # Deterministic mode
    print("\n" + "-" * 70)
    result = wut.is_(df, explain=False)
    print_result(result, "deterministic")

    # LLM mode
    if api_key:
        print("\n" + "-" * 70)
        result = wut.is_(df, explain=True)
        print_result(result, "llm")

    # Aggregated data
    print("\n\n📊 Aggregated Data:")
    summary = df.groupby('product')['revenue'].agg(['sum', 'mean', 'count'])
    print(summary)

    result = wut.is_(summary, explain=False)
    print_result(result, "deterministic")


def demo_4_matplotlib():
    """Demo with Matplotlib figures."""
    print_section("4. Matplotlib Figures")

    try:
        import matplotlib
        matplotlib.use('Agg')  # Non-interactive backend
        import matplotlib.pyplot as plt
        import numpy as np
    except ImportError:
        print("⚠ Matplotlib not installed. Install with: pip install matplotlib")
        return

    # Create a figure with subplots
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))

    # Plot 1: Line plot
    x = np.linspace(0, 10, 100)
    axes[0].plot(x, np.sin(x), label='sin(x)')
    axes[0].plot(x, np.cos(x), label='cos(x)')
    axes[0].set_title('Trigonometric Functions')
    axes[0].set_xlabel('X')
    axes[0].set_ylabel('Y')
    axes[0].legend()
    axes[0].grid(True)

    # Plot 2: Scatter plot
    x = np.random.randn(100)
    y = 2 * x + np.random.randn(100) * 0.5
    axes[1].scatter(x, y, alpha=0.5)
    axes[1].set_title('Linear Relationship')
    axes[1].set_xlabel('X')
    axes[1].set_ylabel('Y')

    plt.tight_layout()

    print("\n📈 Matplotlib Figure (2 subplots created):")

    # Check the figure
    result = wut.is_(fig, explain=False)
    print_result(result, "deterministic")

    if api_key:
        result = wut.is_(fig, explain=True)
        print_result(result, "llm")
        print("\n💡 Notice: The LLM can describe the plots using code history!")

    plt.close(fig)


def demo_5_comparison():
    """Compare deterministic vs LLM modes."""
    print_section("5. Mode Comparison: Deterministic vs LLM")

    try:
        import pandas as pd
        import numpy as np
    except ImportError:
        print("⚠ Pandas required for this demo")
        return

    # Create a complex aggregated DataFrame
    df = pd.DataFrame({
        'product': np.random.choice(['A', 'B', 'C'], 200),
        'region': np.random.choice(['North', 'South', 'East', 'West'], 200),
        'sales': np.random.randint(100, 1000, 200),
        'returns': np.random.randint(0, 50, 200)
    })

    summary = df.groupby(['product', 'region']).agg({
        'sales': ['sum', 'mean'],
        'returns': ['sum', 'mean']
    }).round(2)

    print("\n📊 Complex Aggregated DataFrame:")
    print(summary.head())

    # Deterministic
    print("\n\n🔧 DETERMINISTIC MODE (explain=False):")
    print("-" * 70)
    result_det = wut.is_(summary, explain=False)
    print(result_det.content)
    print("\nCharacteristics:")
    print("  ✓ No API call required")
    print("  ✓ Instant results")
    print("  ✓ Structured, predictable output")
    print("  ✓ Perfect for quick inspection")

    # LLM
    if api_key:
        print("\n\n🤖 LLM MODE (explain=True):")
        print("-" * 70)
        result_llm = wut.is_(summary, explain=True)
        print(result_llm.content)
        print("\nCharacteristics:")
        print("  ✓ Natural language explanation")
        print("  ✓ Context from code history")
        print("  ✓ Semantic understanding")
        print("  ✓ Perfect for LLM consumption")
    else:
        print("\n\n⚠ LLM mode requires OPENROUTER_API_KEY")


def main():
    """Run all demos."""
    print("=" * 70)
    print("  VIBE CHECK - Complete Demo")
    print("  Natural Language Summaries of Python Objects")
    print("=" * 70)

    # Configure
    if api_key:
        wut.configure(openrouter_api_key=api_key)
        print("\n✓ OpenRouter configured - Both modes available")
    else:
        print("\n⚠ No OPENROUTER_API_KEY found")
        print("  Only deterministic mode (explain=False) will work")
        print("  Set API key in .env file or environment variable")

    # Run demos
    try:
        demo_1_builtin_types()
        demo_2_numpy()
        demo_3_pandas()
        demo_4_matplotlib()
        demo_5_comparison()
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
    print("  2. Configure: wut.configure(openrouter_api_key='...')")
    print("  3. Use: wut.is_(obj, explain=True/False)")
    print("\nTwo Modes:")
    print("  • explain=False → Fast, deterministic (no API)")
    print("  • explain=True  → Natural language with LLM")
    print("\nSupported Types:")
    print("  • Built-ins: dict, list, custom classes")
    print("  • NumPy: arrays, matrices")
    print("  • Pandas: DataFrame, Series")
    print("  • Matplotlib: Figure, Axes")
    print("  • And 10+ more libraries!")
    print("\nNext Steps:")
    print("  • Try the Jupyter notebooks: examples/quick_start.ipynb")
    print("  • Read the docs: README.md")
    print("  • Explore adapters: src/wut_is/adapters/")
    print()


if __name__ == "__main__":
    main()
