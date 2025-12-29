"""LLM synthesis and deterministic summary generation."""

import json
from typing import Optional

import httpx

from wut_is.core import APIError, MetaDescription


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
                    "HTTP-Referer": "https://github.com/yourusername/wut_is",
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
    nl = _deterministic_nl(metadata)
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


def _deterministic_nl(metadata: MetaDescription) -> str | None:
    adapter = metadata.get("adapter_used")
    meta = metadata.get("metadata", {})
    obj_type = metadata.get("object_type", "object")
    shape = metadata.get("shape")

    if adapter == "PrimitiveAdapter":
        ptype = meta.get("type")
        if ptype == "int":
            value = meta.get("value")
            special = meta.get("special_form")
            if special:
                return f"The integer {value}, likely a {special.get('type')}."
            return f"An integer with value {value}."
        if ptype == "float":
            value = meta.get("value")
            pattern = meta.get("pattern")
            if pattern:
                return f"A float {value}, likely representing a {pattern}."
            return f"A floating-point number with value {value}."
        if ptype == "bool":
            return f"A boolean value: {meta.get('value')}."
        if ptype == "none":
            return "A None value (null or missing)."
        if ptype == "string":
            if meta.get("document_type"):
                return f"A {meta.get('document_type')} document string ({meta.get('length')} chars)."
            pattern = meta.get("pattern")
            if pattern:
                return f"A string containing a {pattern}: '{meta.get('value')}'."
            return f"A string '{meta.get('value')}' ({meta.get('length')} characters)."
        if ptype == "bytes":
            fmt = meta.get("format")
            if fmt:
                return f"A bytes object containing {fmt} data ({meta.get('length')} bytes)."
            return f"A bytes object of {meta.get('length')} bytes."
        if ptype == "complex":
            return f"A complex number {meta.get('real')} + {meta.get('imag')}i."
        if ptype == "decimal":
            return f"A Decimal value {meta.get('value')} with {meta.get('precision')} digits of precision."
        if ptype == "fraction":
            return f"A Fraction {meta.get('numerator')}/{meta.get('denominator')}."

    if adapter == "CollectionsAdapter":
        ctype = meta.get("type")
        if ctype == "list":
            length = meta.get("length")
            list_type = meta.get("list_type")
            if list_type == "list_of_dicts":
                return f"A list of {length} records with {meta.get('consistent_key_count')} consistent fields."
            if list_type == "ints":
                return f"A list of {length} integers."
            if list_type == "list_of_lists":
                return f"A 2D list with {meta.get('rows')} rows."
            return f"A list of {length} items."
        if ctype == "tuple":
            return f"A tuple of {meta.get('length')} elements."
        if ctype in {"set", "frozenset"}:
            return f"A {ctype} of {meta.get('length')} unique items."
        if ctype in {"dict", "ordered_dict", "defaultdict"}:
            return f"A {ctype} with {meta.get('length')} keys."
        if ctype == "counter":
            return f"A Counter with {meta.get('length')} unique elements totaling {meta.get('total_count')} observations."
        if ctype == "deque":
            return f"A deque of {meta.get('length')} items."
        if ctype == "range":
            return f"A range from {meta.get('start')} to {meta.get('stop')} with step {meta.get('step')}."
        if ctype == "iterator":
            return f"An iterator ({meta.get('name')})."
        if ctype == "generator":
            status = "exhausted" if meta.get("exhausted") else "active"
            return f"A generator '{meta.get('name')}' ({status})."

    if adapter == "H5pyAdapter" and meta.get("type") == "h5py_dataset":
        shape = metadata.get("shape")
        dtype = meta.get("dtype")
        name = meta.get("name")
        chunks = meta.get("chunks")
        compression = meta.get("compression")
        compression_opts = meta.get("compression_opts")
        attrs = meta.get("attrs")
        parts = [f"An HDF5 Dataset '{name}' with shape {shape} and dtype {dtype}."]
        if chunks:
            chunk_desc = f"Chunked: {chunks}."
            if compression:
                level = f" (level {compression_opts})" if compression_opts else ""
                chunk_desc += f" Compression: {compression}{level}."
            parts.append(chunk_desc)
        if attrs:
            parts.append(f"Attributes: {attrs}.")
        if shape and len(shape) >= 3:
            parts.append(
                f"{shape[0]:,} items, {shape[-2]}x{shape[-1]} elements each."
            )
        return " ".join(parts)

    if adapter == "ErrorAdapter" and meta.get("type") == "traceback":
        depth = meta.get("depth")
        frames = meta.get("frames", [])
        parts = [f"A traceback with {depth} frames (most recent last):"]
        for frame in frames:
            parts.append(
                f"→ {frame.get('filename')}:{frame.get('line')} in {frame.get('name')}()"
            )
        last = meta.get("last_frame")
        if last and last.get("code"):
            parts.append(f"Last frame context: '{last.get('code')}'.")
        return "\n".join(parts)

    if adapter == "TextFormatAdapter" and meta.get("format") == "csv":
        rows = meta.get("rows")
        cols = meta.get("columns")
        delimiter = meta.get("delimiter")
        header = meta.get("header", [])
        sample = meta.get("sample_row", [])
        col_types = meta.get("column_types", [])
        parts = [
            f"A CSV string with {rows} rows and {cols} columns ({delimiter}-delimited)."
        ]
        if header:
            parts.append(f"Header: {', '.join(header)}.")
        if sample:
            parts.append(f"Sample: {sample}.")
        if col_types:
            parts.append(f"Column types: {', '.join(col_types)}.")
        parts.append("Best displayed as sortable table.")
        return " ".join(parts)

    if adapter == "TextFormatAdapter" and meta.get("format") == "json":
        keys = meta.get("keys")
        if keys:
            return f"A valid JSON string containing an object with keys: {', '.join(keys)}."
        return "A valid JSON string."

    if adapter == "TextFormatAdapter" and meta.get("format") == "yaml":
        keys = meta.get("keys")
        if keys:
            return f"A valid YAML string containing keys: {', '.join(keys)}."
        return "A valid YAML string."

    if adapter == "TextFormatAdapter" and meta.get("format") == "xml":
        root = meta.get("root_tag")
        return f"A valid XML document with root <{root}>."

    if adapter == "TextFormatAdapter" and meta.get("format") == "html":
        return "An HTML document or fragment."

    if adapter == "SklearnPipelineAdapter" and meta.get("type") == "sklearn_pipeline":
        steps = meta.get("steps", [])
        fitted = meta.get("is_fitted")
        fit_label = "fitted" if fitted else "unfitted"
        parts = [f"A {fit_label} sklearn Pipeline with {len(steps)} steps:"]
        for idx, step in enumerate(steps, start=1):
            parts.append(f"{idx}. '{step['name']}': {step['class']}")
        parts.append("Expects input shape (*, ?), outputs class predictions.")
        return "\n".join(parts)

    if adapter == "ErrorAdapter" and meta.get("type") == "exception":
        return f"An {meta.get('name')} exception: '{meta.get('message')}'."

    if adapter == "NumpyAdapter" and meta.get("type") == "ndarray":
        return f"A numpy array with shape {meta.get('shape', shape)} and dtype {meta.get('dtype')}."
    if adapter == "NumpyAdapter" and meta.get("type") == "numpy_scalar":
        return f"A numpy {meta.get('dtype')} scalar with value {meta.get('value')}."

    if adapter == "PandasAdapter":
        if meta.get("type") == "dataframe":
            return f"A pandas DataFrame with {meta.get('rows')} rows and {meta.get('columns')} columns."
        if meta.get("type") == "series":
            name = meta.get("name") or "unnamed"
            return f"A pandas Series '{name}' with {meta.get('length')} values."
        if meta.get("type") == "index":
            return f"A pandas Index with {meta.get('length')} entries."
        if meta.get("type") == "multiindex":
            return f"A pandas MultiIndex with {meta.get('levels')} levels and {meta.get('length')} entries."
        if meta.get("type") == "timestamp":
            return f"A pandas Timestamp: {meta.get('iso')}."
        if meta.get("type") == "categorical":
            return f"A pandas Categorical with {len(meta.get('categories', []))} categories."

    if adapter == "MatplotlibAdapter":
        if obj_type.endswith("Figure"):
            subplots = meta.get("num_subplots") if meta else None
            return f"A matplotlib figure with {subplots or 'unknown'} subplots."
        return "A matplotlib axes with plotted elements."

    if adapter == "AltairAdapter":
        return f"An Altair chart with mark '{metadata.get('chart_type')}'."

    if adapter == "SeabornAdapter":
        grid = meta.get("grid_type") or "grid"
        return f"A seaborn {grid} with {meta.get('axes_count')} axes."

    if adapter == "PlotlyAdapter":
        return f"A Plotly figure with {meta.get('traces')} traces."

    if adapter == "BokehAdapter":
        return f"A Bokeh figure with {meta.get('renderers')} renderers."

    if adapter == "SklearnAdapter":
        return f"A sklearn model {obj_type}."

    if adapter == "PytorchAdapter":
        return f"A PyTorch tensor with shape {shape}."

    if adapter == "TensorflowAdapter":
        return f"A TensorFlow tensor with shape {meta.get('shape')}."

    if adapter == "JaxAdapter":
        return f"A JAX array with shape {meta.get('shape')}."

    if adapter == "XarrayAdapter":
        return f"An xarray object {obj_type} with shape {shape}."

    if adapter == "NetworkXAdapter":
        return f"A networkx graph with {metadata.get('node_count')} nodes and {metadata.get('edge_count')} edges."

    if adapter == "RequestsAdapter":
        return f"An HTTP response with status {metadata.get('status_code')}."

    if adapter == "PolarsAdapter":
        return f"A Polars DataFrame with shape {metadata.get('shape')}."

    if adapter == "PydanticAdapter":
        return f"A Pydantic model {obj_type}."

    if adapter == "IPythonDisplayAdapter":
        return "An IPython display object."

    if adapter == "AttrsAdapter":
        return f"An attrs class {meta.get('class_name')} with {len(meta.get('fields', []))} fields."

    if adapter == "StructuredAdapter":
        return f"A structured object of type {meta.get('type')}."

    if adapter == "CallableAdapter":
        return f"A callable {meta.get('type')} named {meta.get('name')}."

    if adapter == "AsyncAdapter":
        return f"An async {meta.get('type')} in state {meta.get('state')}."

    if adapter == "DateTimeAdapter":
        return f"A {meta.get('type')} value {meta.get('iso')}." if meta.get("iso") else f"A {meta.get('type')} value."

    if adapter == "PathlibAdapter":
        return f"A path '{meta.get('path')}'."

    if adapter == "RegexAdapter":
        return f"A regex {meta.get('type')}."

    if adapter == "UUIDAdapter":
        return f"A UUID (version {meta.get('version')}): {meta.get('value')}."

    if adapter == "IOAdapter":
        return f"An IO object of type {meta.get('type')}."

    if adapter == "PyArrowAdapter":
        return f"A PyArrow Table with {meta.get('rows')} rows and {meta.get('columns')} columns."

    if adapter == "ScipySparseAdapter":
        return f"A {meta.get('format')} sparse matrix with shape ({meta.get('rows')}, {meta.get('cols')})."

    if adapter == "PILAdapter":
        if meta.get("type") == "pil_image":
            return f"A PIL image {meta.get('width')}x{meta.get('height')} in {meta.get('mode')} mode."
        if meta.get("type") == "pil_image_list":
            return f"A list of {meta.get('count')} PIL images."

    if adapter == "StatsmodelsAdapter":
        return f"A statsmodels results object {meta.get('model_type')}."

    if adapter == "GenericAdapter":
        return f"An object of type {obj_type}."

    return None
