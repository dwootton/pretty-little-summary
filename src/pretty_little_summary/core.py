"""Core types and utilities for Pretty Little Summary."""

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
