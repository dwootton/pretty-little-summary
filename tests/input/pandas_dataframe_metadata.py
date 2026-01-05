ID = "pandas_dataframe_metadata"
TITLE = "Pandas DataFrame"
TAGS = ["pandas", "dataframe"]
REQUIRES = ['pandas']
DISPLAY_INPUT = "pd.DataFrame({'a': [1, 2, None], 'b': ['x', 'y', 'z']})"


def build():
    import pandas as pd

    return pd.DataFrame({"a": [1, 2, None], "b": ["x", "y", "z"]})


def expected(meta):
    from pretty_little_summary.descriptor_utils import format_bytes

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
        for col in col_analysis[:3]:
            name = col.get("name")
            dtype = col.get("dtype")
            col_nulls = col.get("null_count")
            stats = col.get("stats")
            cardinality = col.get("cardinality")
            details = []
            if dtype:
                details.append(dtype)
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
        parts.append(f"Sample row: {sample_rows[0]}.")
    elif meta["metadata"].get("sample_rows_omitted"):
        parts.append("Sample rows omitted for size/perf.")
    return " ".join(parts)
