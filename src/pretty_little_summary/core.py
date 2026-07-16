"""Core types and utilities for Pretty Little Summary."""

from typing import Any, TypedDict


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
    shape: tuple[int, ...] | None
    columns: list[str] | None
    dtypes: dict[str, str] | None
    sample_data: str | None  # Markdown table or JSON

    # Metadata extraction
    metadata: dict[str, Any] | None  # Generic metadata dict

    # Graph/Network specific
    node_count: int | None
    edge_count: int | None
    density: float | None

    # ML Model specific
    parameters: dict[str, Any] | None
    parameter_count: int | None
    is_fitted: bool | None

    # Visualization specific
    chart_type: str | None
    spec: dict[str, Any] | None  # Altair/Vega spec
    visual_elements: dict[str, Any] | None  # Matplotlib elements
    style: str | None  # e.g., "imperative" for matplotlib

    # HTTP Response specific
    status_code: int | None
    url: str | None
    headers: dict[str, str] | None

    # Schema-specific (Pydantic, etc.)
    schema: dict[str, Any] | None
    fields: dict[str, Any] | None

    # Additional context
    warnings: list[str] | None  # Any issues during introspection
    raw_repr: str | None  # Fallback string representation


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
        var_name: str | None = None, max_lines: int = 10
    ) -> list[str] | None:
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
