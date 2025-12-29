"""
Pretty Little Summary: Natural language summaries of Python objects for LLM consumption.

Usage:
    import pretty_little_summary as pls

    # Configure (or set OPENROUTER_API_KEY env var)
    pls.configure(openrouter_api_key="sk-or-...")

    # Get summary of any object
    result = pls.describe(my_dataframe)

    print(result.content)  # Natural language summary
    print(result.meta)     # Structured metadata
    print(result.history)  # Code history (if in Jupyter)

    # Deterministic mode (no LLM call)
    result = pls.describe(my_dataframe, explain=False)
"""

from pretty_little_summary.adapters._base import list_available_adapters
from pretty_little_summary.api import Description, describe
from pretty_little_summary.core import configure

__version__ = "0.1.0"
__all__ = ["describe", "configure", "Description", "list_available_adapters"]
