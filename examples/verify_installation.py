#!/usr/bin/env python3
"""
Verify pretty_little_summary installation.

Run this script to check if pretty_little_summary is installed correctly and
which optional adapters are available.

Usage:
    python examples/verify_installation.py
"""

import sys


def check_pretty_little_summary():
    """Check if pretty_little_summary is installed."""
    try:
        import pretty_little_summary as pls

        print("✅ pretty_little_summary is installed")
        print(f"   Version: {pls.__version__}")
        return True
    except ImportError as e:
        print("❌ pretty_little_summary is NOT installed")
        print(f"   Error: {e}")
        print("\n   To install:")
        print("   1. cd /path/to/pretty_little_summary")
        print("   2. pip install -e .")
        print("   3. Restart your Python kernel/interpreter")
        return False


def check_optional_libraries():
    """Check which optional data libraries are available."""
    print("\nOptional Libraries (for adapters):")

    libs = {
        "pandas": "DataFrame, Series",
        "numpy": "ndarray",
        "polars": "DataFrame, LazyFrame",
        "pyarrow": "Table",
        "matplotlib": "Figure, Axes",
        "seaborn": "Axes",
        "altair": "Chart",
        "plotly": "Figure",
        "bokeh": "Figure",
        "sklearn": "ML models",
        "torch": "nn.Module",
        "tensorflow": "Tensor, Model",
        "jax": "Array",
        "xarray": "DataArray, Dataset",
        "pydantic": "BaseModel",
        "networkx": "Graph",
        "scipy": "Sparse matrices",
        "statsmodels": "Statistical models",
        "h5py": "File",
        "PIL": "Images",
        "attrs": "Attrs classes",
        "requests": "Response",
        "IPython": "Notebook history",
    }

    available = []
    missing = []

    for lib_name, description in libs.items():
        try:
            __import__(lib_name)
            print(f"  ✅ {lib_name:15s} - {description}")
            available.append(lib_name)
        except ImportError:
            print(f"  ⚪ {lib_name:15s} - {description} (optional)")
            missing.append(lib_name)

    return available, missing


def test_basic_functionality():
    """Test basic pretty_little_summary functionality."""
    print("\nBasic Functionality Test:")

    try:
        import pretty_little_summary as pls

        test_obj = {"name": "test", "value": 42}
        result = pls.describe(test_obj)

        assert result.content is not None
        assert result.meta is not None
        assert "object_type" in result.meta
        assert "adapter_used" in result.meta

        print("  ✅ Basic describe() works")
        print(f"     Result: {result.content[:60]}...")
        return True
    except Exception as e:
        print(f"  ❌ Basic describe() failed: {e}")
        return False


def main():
    """Run all verification checks."""
    print("=" * 70)
    print("  Pretty Little Summary Installation Verification")
    print("=" * 70)

    if not check_pretty_little_summary():
        sys.exit(1)

    available, missing = check_optional_libraries()
    func_ok = test_basic_functionality()

    print("\n" + "=" * 70)
    print("  Summary")
    print("=" * 70)

    if func_ok:
        print("\n✅ pretty_little_summary is properly installed and functional!")
    else:
        print("\n⚠ pretty_little_summary has some issues")

    print(f"\nAvailable adapters: {len(available)}/{len(available) + len(missing)}")
    if available:
        print(f"  Installed: {', '.join(available)}")
    if missing:
        print(f"  Missing (optional): {', '.join(missing)}")
        print("\n  To install all: pip install -e '.[all]'")

    print("\n" + "=" * 70)
    print("\nNext Steps:")
    print("  1. Run a demo: python examples/complete_demo.py")
    print("  2. Read the docs: cat README.md")
    print()


if __name__ == "__main__":
    main()
