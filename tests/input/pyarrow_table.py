ID = "pyarrow_table"
TITLE = "PyArrow Table"
TAGS = ["pyarrow", "table"]
REQUIRES = ['pyarrow']
DISPLAY_INPUT = "pa.table({'a': [1, 2], 'b': ['x', 'y']})"


def build():
    import pyarrow as pa

    return pa.table({"a": [1, 2], "b": ["x", "y"]})


def expected(meta):
    parts = [
        f"A PyArrow Table with {meta['metadata']['rows']} rows and {meta['metadata']['columns']} columns."
    ]
    schema = meta["metadata"].get("schema") or {}
    if schema:
        cols = []
        for name, dtype in list(schema.items())[:3]:
            cols.append(f"{name} ({dtype})")
        if cols:
            parts.append(f"Schema: {', '.join(cols)}.")
    memory = meta["metadata"].get("memory")
    if memory:
        parts.append(f"Memory: {memory}.")
    sample_rows = meta["metadata"].get("sample_rows")
    if sample_rows:
        parts.append(f"Sample row: {sample_rows[0]}.")
    elif meta["metadata"].get("sample_rows_omitted"):
        parts.append("Sample rows omitted for size/perf.")
    return " ".join(parts)
