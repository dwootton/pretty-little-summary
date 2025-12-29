#!/usr/bin/env python3
"""
Verify wut_is installation

Run this script to check if wut_is is installed correctly and what features are available.

Usage:
    python examples/verify_installation.py
"""

import sys


def check_wut_is():
    """Check if wut_is is installed."""
    try:
        import wut_is as wut
        print("✅ wut_is is installed")
        print(f"   Version: {wut.__version__}")
        return True
    except ImportError as e:
        print("❌ wut_is is NOT installed")
        print(f"   Error: {e}")
        print("\n   To install:")
        print("   1. cd /path/to/wut_is")
        print("   2. pip install -e .")
        print("   3. Restart your Python kernel/interpreter")
        return False


def check_core_dependencies():
    """Check if core dependencies are installed."""
    print("\nCore Dependencies:")

    deps = {
        'httpx': 'Required for OpenRouter API calls',
        'dotenv': 'Required for .env configuration'
    }

    all_ok = True
    for module_name, description in deps.items():
        try:
            if module_name == 'dotenv':
                __import__('dotenv')
            else:
                __import__(module_name)
            print(f"  ✅ {module_name:15s} - {description}")
        except ImportError:
            print(f"  ❌ {module_name:15s} - {description} (MISSING)")
            all_ok = False

    return all_ok


def check_optional_libraries():
    """Check which optional data libraries are available."""
    print("\nOptional Libraries (for adapters):")

    libs = {
        'pandas': 'DataFrame, Series',
        'numpy': 'ndarray (used by generic adapter)',
        'polars': 'DataFrame, LazyFrame',
        'matplotlib': 'Figure, Axes',
        'altair': 'Chart',
        'sklearn': 'ML models',
        'torch': 'nn.Module',
        'xarray': 'DataArray, Dataset',
        'pydantic': 'BaseModel',
        'networkx': 'Graph',
        'requests': 'Response',
    }

    available = []
    missing = []

    for lib_name, description in libs.items():
        try:
            if lib_name == 'sklearn':
                __import__('sklearn')
            else:
                __import__(lib_name)
            print(f"  ✅ {lib_name:15s} - {description}")
            available.append(lib_name)
        except ImportError:
            print(f"  ⚪ {lib_name:15s} - {description} (optional)")
            missing.append(lib_name)

    return available, missing


def check_api_configuration():
    """Check if OpenRouter API is configured."""
    print("\nAPI Configuration:")

    import os
    from dotenv import load_dotenv

    # Try to load .env
    load_dotenv()

    api_key = os.getenv('OPENROUTER_API_KEY')

    if api_key:
        # Mask the key for security
        masked_key = api_key[:10] + '...' + api_key[-10:]
        print(f"  ✅ OPENROUTER_API_KEY found: {masked_key}")
        print("     LLM mode (explain=True) will work!")
        return True
    else:
        print("  ⚪ OPENROUTER_API_KEY not found")
        print("     Only deterministic mode (explain=False) will work")
        print("\n     To enable LLM mode:")
        print("     1. Get an API key from https://openrouter.ai")
        print("     2. Set it in .env file: OPENROUTER_API_KEY=sk-or-...")
        print("     3. Or export it: export OPENROUTER_API_KEY='sk-or-...'")
        return False


def test_basic_functionality():
    """Test basic wut_is functionality."""
    print("\nBasic Functionality Test:")

    try:
        import wut_is as wut

        # Test deterministic mode with a simple dict
        test_obj = {'name': 'test', 'value': 42}
        result = wut.is_(test_obj, explain=False)

        assert result.content is not None
        assert result.meta is not None
        assert 'object_type' in result.meta
        assert 'adapter_used' in result.meta

        print("  ✅ Basic check() works")
        print(f"     Result: {result.content[:60]}...")
        return True
    except Exception as e:
        print(f"  ❌ Basic check() failed: {e}")
        return False


def main():
    """Run all verification checks."""
    print("=" * 70)
    print("  Wut Is Installation Verification")
    print("=" * 70)

    # Check wut_is installation
    if not check_wut_is():
        sys.exit(1)

    # Check dependencies
    core_ok = check_core_dependencies()

    # Check optional libraries
    available, missing = check_optional_libraries()

    # Check API configuration
    api_ok = check_api_configuration()

    # Test basic functionality
    func_ok = test_basic_functionality()

    # Summary
    print("\n" + "=" * 70)
    print("  Summary")
    print("=" * 70)

    if core_ok and func_ok:
        print("\n✅ wut_is is properly installed and functional!")
    else:
        print("\n⚠️  wut_is has some issues")

    print(f"\nAvailable adapters: {len(available)}/11")
    if available:
        print(f"  Installed: {', '.join(available)}")
    if missing:
        print(f"  Missing (optional): {', '.join(missing)}")
        print(f"\n  To install all: pip install -e '.[all]'")

    if api_ok:
        print("\n🤖 LLM mode: ENABLED (explain=True)")
    else:
        print("\n🔧 LLM mode: DISABLED (only explain=False available)")

    print("\n" + "=" * 70)
    print("\nNext Steps:")
    print("  1. Try the quick start: jupyter notebook examples/quick_start.ipynb")
    print("  2. Run a demo: python examples/complete_demo.py")
    print("  3. Read the docs: cat README.md")
    print()


if __name__ == "__main__":
    main()
