ID = "pandas_dataframe_metadata"
TITLE = "Pandas DataFrame"
TAGS = ["pandas", "dataframe"]
REQUIRES = ['pandas']
DISPLAY_INPUT = "pd.DataFrame({'a': [1, 2, None], 'b': ['x', 'y', 'z']})"


def build():
    import pandas as pd

    return pd.DataFrame({"a": [1, 2, None], "b": ["x", "y", "z"]})


def expected(meta):
    from pretty_little_summary.adapters.pandas import _select_featured_columns
    from pretty_little_summary.descriptor_utils import format_bytes, truncate_row_keys

    parts = [
        f"A pandas DataFrame with {meta['metadata']['rows']} rows and {meta['metadata']['columns']} columns."
    ]
    null_count = meta["metadata"].get("null_count")
    if null_count is not None:
        parts.append(f"Nulls: {null_count}.")
    memory_bytes = meta["metadata"].get("memory_bytes")
    if memory_bytes is not None:
        parts.append(f"Memory: {format_bytes(memory_bytes)}.")
    col_analysis = meta["metadata"].get("column_analysis") or []
    if col_analysis:
        cols = []
        for col in _select_featured_columns(col_analysis):
            name = col.get("name")
            dtype = col.get("dtype")
            col_nulls = col.get("null_count")
            stats = col.get("stats")
            cardinality = col.get("cardinality")
            mixed_types = col.get("mixed_types")
            details = []
            if dtype:
                details.append(dtype)
            if mixed_types:
                details.append(f"mixed types: {', '.join(mixed_types)}")
            if col_nulls:
                details.append(f"{col_nulls} nulls")
            if stats:
                details.append(f"stats: {stats}")
            elif cardinality:
                details.append(f"cardinality: {cardinality}")
            cols.append(f"{name} ({', '.join(details)})" if details else f"{name}")
        if cols:
            parts.append(f"Columns: {', '.join(cols)}.")
    sample_rows = meta["metadata"].get("sample_rows")
    if sample_rows:
        parts.append(f"Sample row: {truncate_row_keys(sample_rows[0])}.")
    return " ".join(parts)
