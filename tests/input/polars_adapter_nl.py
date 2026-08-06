ID = "polars_adapter_nl"
TITLE = "Polars DataFrame"
TAGS = ["polars", "dataframe"]
REQUIRES = ['polars']
DISPLAY_INPUT = "pl.DataFrame({'a': [1, 2], 'b': ['x', 'y']})"


def build():
    import polars as pl

    return pl.DataFrame({"a": [1, 2], "b": ["x", "y"]})


def expected(meta):
    from pretty_little_summary.descriptor_utils import truncate_row_keys

    parts = [f"A Polars DataFrame with shape {meta.get('shape')}."]
    schema = meta.get("schema") or {}
    if schema:
        cols = []
        for name, dtype in list(schema.items())[:3]:
            cols.append(f"{name} ({dtype})")
        if cols:
            parts.append(f"Schema: {', '.join(cols)}.")
    sample_rows = meta.get("metadata", {}).get("sample_rows")
    if sample_rows:
        parts.append(f"Sample row: {truncate_row_keys(sample_rows[0])}.")
    return " ".join(parts)
