"""
Wut Is: Natural language summaries of Python objects for LLM consumption.

Usage:
    import wut_is as wut

    # Configure (or set OPENROUTER_API_KEY env var)
    wut.configure(openrouter_api_key="sk-or-...")

    # Get summary of any object
    result = wut.is_(my_dataframe)
    # Or use the convenient wrapper:
    result = wut.is(my_dataframe)

    print(result.content)  # Natural language summary
    print(result.meta)     # Structured metadata
    print(result.history)  # Code history (if in Jupyter)

    # Deterministic mode (no LLM call)
    result = wut.is_(my_dataframe, explain=False)
"""

from wut_is.adapters._base import list_available_adapters
from wut_is.api import WutIs, is_ as is_
from wut_is.core import configure

# Note: We use is_() since 'is' is a Python keyword and can't be used as a function name
# Usage: wut.is_(obj) or wut.is_(obj, explain=False)

__version__ = "0.1.0"
__all__ = ["is_", "configure", "WutIs", "list_available_adapters"]
