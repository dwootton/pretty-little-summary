"""LLM synthesis and deterministic summary generation."""

import json
from typing import Optional

import httpx

from pretty_little_summary.core import APIError, MetaDescription


class OpenRouterClient:
    """
    Client for OpenRouter API.

    Handles LLM synthesis of metadata and history into natural language summaries.
    """

    BASE_URL = "https://openrouter.ai/api/v1/chat/completions"

    def __init__(self, api_key: str, model: str):
        """
        Initialize OpenRouter client.

        Args:
            api_key: OpenRouter API key
            model: Model to use (e.g., "anthropic/claude-3.5-sonnet")
        """
        self.api_key = api_key
        self.model = model

    def synthesize(
        self, metadata: MetaDescription, history: Optional[list[str]] = None
    ) -> str:
        """
        Generate natural language summary from metadata and history.

        Args:
            metadata: Extracted object metadata
            history: IPython history lines (if available)

        Returns:
            Natural language summary string

        Raises:
            APIError: If the API call fails
        """
        try:
            response = httpx.post(
                self.BASE_URL,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "HTTP-Referer": "https://github.com/yourusername/pretty_little_summary",
                    "X-Title": "Vibe Check",
                },
                json=self._build_request(metadata, history),
                timeout=30.0,
            )
            response.raise_for_status()

            result = response.json()
            return result["choices"][0]["message"]["content"]

        except httpx.HTTPStatusError as e:
            raise APIError(
                f"OpenRouter API error: {e.response.status_code} - {e.response.text}"
            )
        except httpx.TimeoutException:
            raise APIError("OpenRouter API timeout")
        except Exception as e:
            raise APIError(f"Unexpected error calling OpenRouter: {e}")

    def _build_request(
        self, metadata: MetaDescription, history: Optional[list[str]]
    ) -> dict:
        """Build OpenRouter API request payload."""
        history_section = ""
        if history:
            history_lines = "\n".join(history)
            history_section = f"""
Code History (last {len(history)} relevant lines):
```python
{history_lines}
```

Note: For imperative visualizations (matplotlib), prioritize this history to understand user intent.
"""

        system_message = f"""You are an expert Python data analyst helping users understand their objects.

Your task: Synthesize metadata and code history into a concise, natural language summary.

Guidelines:
- Focus on what the object IS and what it REPRESENTS
- If history is available, infer the user's INTENT from their code
- For visualizations, describe what's being shown
- For models, explain the type and configuration
- For data, summarize shape, content, and quality
- Be conversational but precise
- Limit response to 3-4 sentences

Metadata:
{self._format_metadata(metadata)}

{history_section}

Provide a brief, insightful summary suitable for an LLM that will use this object in further analysis."""

        return {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_message},
                {"role": "user", "content": "Please provide a summary of this object."},
            ],
            "max_tokens": 300,  # Keep summaries concise
            "temperature": 0.7,
        }

    def _format_metadata(self, meta: MetaDescription) -> str:
        """Convert MetaDescription to readable JSON."""
        return json.dumps(meta, indent=2, default=str)


def deterministic_summary(
    metadata: MetaDescription, history: Optional[list[str]] = None
) -> str:
    """
    Generate a deterministic summary without LLM call.

    This is used when explain=False. It formats the metadata into a readable
    text representation without requiring an API call.

    Args:
        metadata: Extracted object metadata
        history: IPython history lines (if available, not heavily used here)

    Returns:
        Formatted string summary

    Example:
        >>> meta = {"object_type": "pandas.DataFrame", "shape": (100, 5)}
        >>> deterministic_summary(meta)
        "pandas.DataFrame | Shape: (100, 5)"
    """
    nl = metadata.get("nl_summary")
    if nl:
        return nl

    lines = []

    # Object type (always present)
    obj_type = metadata.get("object_type", "Unknown")
    lines.append(f"{obj_type}")

    # Shape
    if "shape" in metadata:
        shape = metadata["shape"]
        lines.append(f"Shape: {shape}")

    # Columns (for DataFrames)
    if "columns" in metadata:
        columns = metadata["columns"]
        if columns:
            # Convert columns to strings (handles MultiIndex tuples, etc.)
            col_strs = [str(c) for c in columns[:5]]
            col_preview = ", ".join(col_strs)
            if len(columns) > 5:
                col_preview += f", ... ({len(columns)} total)"
            lines.append(f"Columns: {col_preview}")

    # Dtypes (for DataFrames)
    if "dtypes" in metadata:
        dtypes = metadata["dtypes"]
        if dtypes and len(dtypes) <= 3:
            lines.append(f"Types: {', '.join(f'{k}:{v}' for k, v in list(dtypes.items())[:3])}")

    # Node/Edge counts (for graphs)
    if "node_count" in metadata:
        lines.append(f"Nodes: {metadata['node_count']}")
    if "edge_count" in metadata:
        lines.append(f"Edges: {metadata['edge_count']}")

    # Parameter count (for ML models)
    if "parameter_count" in metadata:
        lines.append(f"Parameters: {metadata['parameter_count']:,}")

    # Is fitted (for sklearn)
    if "is_fitted" in metadata:
        status = "fitted" if metadata["is_fitted"] else "not fitted"
        lines.append(f"Status: {status}")

    # HTTP status (for requests)
    if "status_code" in metadata:
        lines.append(f"Status: {metadata['status_code']}")
    if "url" in metadata:
        url = metadata["url"]
        if len(url) > 50:
            url = url[:50] + "..."
        lines.append(f"URL: {url}")

    # Visualization metadata
    if "chart_type" in metadata:
        lines.append(f"Chart: {metadata['chart_type']}")
    if "visual_elements" in metadata:
        elements = metadata["visual_elements"]
        if isinstance(elements, dict):
            title = elements.get("title")
            if title:
                lines.append(f"Title: {title}")
            plot_types = elements.get("plot_types")
            if plot_types:
                lines.append(f"Plot types: {', '.join(plot_types)}")

    # GenericAdapter metadata (for built-in types)
    if "metadata" in metadata:
        gen_meta = metadata["metadata"]

        # Length (for collections)
        if "length" in gen_meta:
            lines.append(f"Length: {gen_meta['length']}")

        # Keys (for dicts)
        if "keys" in gen_meta:
            keys = gen_meta["keys"]
            key_preview = ", ".join(str(k) for k in keys[:5])
            if len(keys) > 5:
                key_preview += "..."
            lines.append(f"Keys: {key_preview}")

        # Sample items (for dicts/lists)
        if "sample_items" in gen_meta and isinstance(gen_meta["sample_items"], dict):
            # Dict sample
            items_str = ", ".join(f"{k}: {v}" for k, v in list(gen_meta["sample_items"].items())[:3])
            lines.append(f"Sample: {{{items_str}}}")

        # Element types (for lists/tuples/sets)
        if "element_types" in gen_meta:
            types_str = ", ".join(gen_meta["element_types"])
            lines.append(f"Element types: {types_str}")

        # Value (for simple types)
        if "value" in gen_meta:
            val = gen_meta["value"]
            val_str = str(val)
            if len(val_str) > 50:
                val_str = val_str[:50] + "..."
            lines.append(f"Value: {val_str}")

        # Preview (for strings)
        if "preview" in gen_meta:
            preview = gen_meta["preview"]
            if len(preview) > 50:
                preview = preview[:50] + "..."
            lines.append(f'"{preview}"')

        # Attributes (for custom objects)
        if "attributes" in gen_meta:
            attrs = gen_meta["attributes"]
            attr_preview = ", ".join(attrs[:5])
            if len(attrs) > 5:
                attr_preview += "..."
            lines.append(f"Attributes: {attr_preview}")

        # Common descriptor fields for stdlib adapters
        if "type" in gen_meta:
            lines.append(f"Type: {gen_meta['type']}")
        if "name" in gen_meta:
            lines.append(f"Name: {gen_meta['name']}")
        if "path" in gen_meta:
            lines.append(f"Path: {gen_meta['path']}")
        if "iso" in gen_meta:
            lines.append(f"ISO: {gen_meta['iso']}")
        if "timezone" in gen_meta and gen_meta["timezone"]:
            lines.append(f"Timezone: {gen_meta['timezone']}")
        if "pattern" in gen_meta:
            lines.append(f"Pattern: {gen_meta['pattern']}")
        if "document_type" in gen_meta:
            lines.append(f"Doc type: {gen_meta['document_type']}")
        if "format" in gen_meta:
            lines.append(f"Format: {gen_meta['format']}")
        if "stats" in gen_meta:
            lines.append(f"Stats: {gen_meta['stats']}")
        if "cardinality" in gen_meta:
            lines.append(f"Cardinality: {gen_meta['cardinality']}")
        if "null_count" in gen_meta:
            lines.append(f"Nulls: {gen_meta['null_count']}")
        if "memory_bytes" in gen_meta:
            lines.append(f"Memory: {gen_meta['memory_bytes']} bytes")
        if "dtype" in gen_meta:
            lines.append(f"Dtype: {gen_meta['dtype']}")
        if "shape" in gen_meta:
            lines.append(f"Shape: {gen_meta['shape']}")
        if "trace_types" in gen_meta:
            lines.append(f"Traces: {', '.join(gen_meta['trace_types'])}")
        if "traces" in gen_meta:
            lines.append(f"Trace count: {gen_meta['traces']}")
        if "grid_type" in gen_meta:
            lines.append(f"Grid: {gen_meta['grid_type']}")
        if "axes_count" in gen_meta:
            lines.append(f"Axes: {gen_meta['axes_count']}")
    # Warnings
    if "warnings" in metadata and metadata["warnings"]:
        lines.append(f"Warnings: {len(metadata['warnings'])} issue(s)")

    # Adapter used
    adapter = metadata.get("adapter_used", "Unknown")
    lines.append(f"[via {adapter}]")

    return " | ".join(lines)
