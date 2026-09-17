"""
Pretty Little Summary: Automatic structured summaries of Python objects.

Usage:
    import pretty_little_summary as pls

    # Get summary of any object
    result = pls.describe(my_dataframe)

    print(result.content)  # Structured summary
    print(result.meta)     # Detailed metadata
    print(result.history)  # Code history (if in Jupyter)
"""

from pretty_little_summary.adapters._base import list_available_adapters
from pretty_little_summary.api import Description, describe
from pretty_little_summary.file_capabilities import requirements_for_path
from pretty_little_summary.relevance import FocusedProfile, focus_profile

__version__ = "0.3.1"
__all__ = [
    "Description",
    "FocusedProfile",
    "describe",
    "focus_profile",
    "list_available_adapters",
    "requirements_for_path",
]
