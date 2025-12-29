"""Core types and utilities for wut_is."""

import os
from pathlib import Path
from typing import Any, Optional, TypedDict


class MetaDescription(TypedDict, total=False):
    """
    JSON-serializable metadata about an object.

    This TypedDict uses total=False to allow partial metadata
    when extraction fails for some fields.
    """

    # Common fields (present for all objects)
    object_type: str  # e.g., "pandas.DataFrame"
    adapter_used: str  # e.g., "PandasAdapter"

    # Data structure fields
    shape: Optional[tuple[int, ...]]
    columns: Optional[list[str]]
    dtypes: Optional[dict[str, str]]
    sample_data: Optional[str]  # Markdown table or JSON

    # Metadata extraction
    metadata: Optional[dict[str, Any]]  # Generic metadata dict

    # Graph/Network specific
    node_count: Optional[int]
    edge_count: Optional[int]
    density: Optional[float]

    # ML Model specific
    parameters: Optional[dict[str, Any]]
    parameter_count: Optional[int]
    is_fitted: Optional[bool]

    # Visualization specific
    chart_type: Optional[str]
    spec: Optional[dict[str, Any]]  # Altair/Vega spec
    visual_elements: Optional[dict[str, Any]]  # Matplotlib elements
    style: Optional[str]  # e.g., "imperative" for matplotlib

    # HTTP Response specific
    status_code: Optional[int]
    url: Optional[str]
    headers: Optional[dict[str, str]]

    # Schema-specific (Pydantic, etc.)
    schema: Optional[dict[str, Any]]
    fields: Optional[dict[str, Any]]

    # Additional context
    warnings: Optional[list[str]]  # Any issues during introspection
    raw_repr: Optional[str]  # Fallback string representation


class Config:
    """
    Singleton configuration manager for wut_is.

    Priority: 1) Direct configure() calls, 2) Environment variables, 3) Defaults
    """

    _instance: Optional["Config"] = None

    def __new__(cls) -> "Config":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self) -> None:
        """Load configuration from environment."""
        # Try to load .env file if python-dotenv available
        try:
            from dotenv import load_dotenv

            load_dotenv()
        except ImportError:
            pass

        # Load from environment
        self.openrouter_api_key: Optional[str] = os.getenv("OPENROUTER_API_KEY")
        self.openrouter_model: str = os.getenv(
            "VIBECHECK_MODEL", "anthropic/claude-3.5-sonnet"
        )
        self.max_history_lines: int = int(os.getenv("VIBECHECK_MAX_HISTORY", "10"))
        self.debug_mode: bool = os.getenv("VIBECHECK_DEBUG", "").lower() == "true"

    @classmethod
    def get_instance(cls) -> "Config":
        """Get singleton instance."""
        return cls()

    def update(
        self,
        openrouter_api_key: Optional[str] = None,
        model: Optional[str] = None,
        max_history_lines: Optional[int] = None,
        debug: Optional[bool] = None,
    ) -> None:
        """Update configuration values."""
        if openrouter_api_key is not None:
            self.openrouter_api_key = openrouter_api_key
        if model is not None:
            self.openrouter_model = model
        if max_history_lines is not None:
            self.max_history_lines = max_history_lines
        if debug is not None:
            self.debug_mode = debug


class HistorySlicer:
    """
    Extract IPython/Jupyter history for narrative provenance.

    This class provides static methods to detect the IPython environment
    and extract relevant code history for understanding how objects were created.
    """

    @staticmethod
    def is_ipython_environment() -> bool:
        """
        Check if running in IPython/Jupyter.

        Returns:
            True if in IPython/Jupyter, False otherwise
        """
        try:
            from IPython import get_ipython

            return get_ipython() is not None
        except ImportError:
            return False

    @staticmethod
    def get_history(
        var_name: Optional[str] = None, max_lines: int = 10
    ) -> Optional[list[str]]:
        """
        Extract relevant history lines.

        Args:
            var_name: Filter for lines containing this variable (optional)
            max_lines: Maximum history lines to return

        Returns:
            List of history strings, or None if not in IPython
        """
        if not HistorySlicer.is_ipython_environment():
            return None

        try:
            from IPython import get_ipython

            ip = get_ipython()
            if ip is None:
                return None

            # Access input history (_ih)
            history = ip.user_ns.get("_ih", [])

            if not history:
                return None

            # Filter history
            if var_name:
                filtered = HistorySlicer._filter_history(history, var_name)
            else:
                # If no var_name, just get the last N lines
                filtered = [h for h in history if h.strip() and not h.startswith(("%", "!"))]

            # Return last max_lines entries
            return filtered[-max_lines:] if filtered else None

        except Exception:
            # Graceful degradation
            return None

    @staticmethod
    def _filter_history(history: list[str], var_name: str) -> list[str]:
        """
        Filter history for relevant lines using simple string matching.

        Args:
            history: List of history lines
            var_name: Variable name to filter for

        Returns:
            Filtered list of history lines
        """
        filtered = []
        for line in history:
            # Skip empty lines and magic commands
            if not line.strip() or line.startswith(("%", "!")):
                continue

            # Case-sensitive substring search
            if var_name in line:
                filtered.append(line)

        return filtered


class VibecheckError(Exception):
    """Base exception for wut_is."""

    pass


class ConfigurationError(VibecheckError):
    """Configuration is invalid or missing."""

    pass


class APIError(VibecheckError):
    """OpenRouter API error."""

    pass


def configure(
    openrouter_api_key: Optional[str] = None,
    model: Optional[str] = None,
    max_history_lines: Optional[int] = None,
    debug: bool = False,
) -> None:
    """
    Configure wut_is settings.

    Args:
        openrouter_api_key: OpenRouter API key
        model: Model to use (default: anthropic/claude-3.5-sonnet)
        max_history_lines: Max history lines to include (default: 10)
        debug: Enable debug logging (default: False)

    Example:
        >>> import pretty_little_summary as vibe
        >>> vibe.configure(openrouter_api_key="sk-or-...")
    """
    config = Config.get_instance()
    config.update(
        openrouter_api_key=openrouter_api_key,
        model=model,
        max_history_lines=max_history_lines,
        debug=debug,
    )
