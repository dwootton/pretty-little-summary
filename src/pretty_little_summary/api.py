"""Main API entry point for pretty_little_summary."""

from dataclasses import dataclass
from typing import Any, Optional

from pretty_little_summary.adapters import dispatch_adapter
from pretty_little_summary.core import Config, ConfigurationError, HistorySlicer
from pretty_little_summary.synthesizer import OpenRouterClient, deterministic_summary


@dataclass
class Description:
    """
    Result object from pls.describe().

    Attributes:
        content: Natural language explanation of what the object is
        meta: Structured facts (Schema, Stats, Adapter Used)
        history: Code history if available from IPython/Jupyter
    """

    content: str
    meta: dict
    history: Optional[list[str]]


def describe(obj: Any, explain: bool = True, name: Optional[str] = None) -> Description:
    """
    Generate a summary of any Python object.

    This is the main entry point for pretty_little_summary. It:
    1. Extracts metadata using adapters
    2. Retrieves code history (if in IPython/Jupyter)
    3. Synthesizes a summary (via LLM if explain=True, deterministic if explain=False)

    Args:
        obj: Any Python object to analyze
        explain: If True, use LLM to generate natural language summary.
                 If False, generate deterministic summary (no API call).
        name: Optional variable name for history filtering.
              If None, attempts to auto-detect from calling context.

    Returns:
        Description object with content, meta, and history attributes

    Raises:
        ConfigurationError: If OpenRouter API key not configured (only when explain=True)
        APIError: If LLM synthesis fails (only when explain=True)

    Examples:
        >>> import pretty_little_summary as pls
        >>> import pandas as pd
        >>> pls.configure(openrouter_api_key="sk-or-...")
        >>> df = pd.read_csv("data.csv")
        >>> result = pls.describe(df)
        >>> print(result.content)
        "This is a pandas DataFrame with 1000 rows and 5 columns..."

        >>> # Deterministic mode (no LLM call)
        >>> result = pls.describe(df, explain=False)
        >>> print(result.content)
        "pandas.DataFrame | Shape: (1000, 5) | Columns: a, b, c, d, e"
    """
    # Get config
    config = Config.get_instance()

    # Validate configuration (only needed if explain=True)
    if explain and not config.openrouter_api_key:
        raise ConfigurationError(
            "OpenRouter API key not configured. "
            "Set OPENROUTER_API_KEY environment variable or call "
            "pretty_little_summary.configure(openrouter_api_key='...')"
        )

    # Auto-detect variable name if not provided
    if name is None:
        name = _try_get_variable_name(obj)

    # Extract metadata using adapter system
    metadata = dispatch_adapter(obj)

    # Get history if available
    history: Optional[list[str]] = None
    if HistorySlicer.is_ipython_environment():
        history = HistorySlicer.get_history(
            var_name=name, max_lines=config.max_history_lines
        )

    # Generate summary
    if explain:
        # Use LLM synthesis
        client = OpenRouterClient(
            api_key=config.openrouter_api_key,  # type: ignore
            model=config.openrouter_model,
        )
        content = client.synthesize(metadata, history)
    else:
        # Use deterministic summary
        content = deterministic_summary(metadata, history)

    # Return Description object
    return Description(content=content, meta=metadata, history=history)


def _try_get_variable_name(obj: Any) -> Optional[str]:
    """
    Attempt to auto-detect variable name from IPython namespace.

    Strategy:
    - Access get_ipython().user_ns (namespace dict)
    - Find variable(s) that reference the same object (using `is`)
    - Return the first match (or None)

    This is best-effort; may not work for complex cases.

    Args:
        obj: Object to find variable name for

    Returns:
        Variable name if found, None otherwise
    """
    try:
        from IPython import get_ipython

        ip = get_ipython()
        if ip is None:
            return None

        # Search namespace for matching object
        for var_name, var_obj in ip.user_ns.items():
            if var_obj is obj and not var_name.startswith("_"):
                return var_name

    except (ImportError, AttributeError):
        pass

    return None
