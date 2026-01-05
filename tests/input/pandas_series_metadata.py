ID = "pandas_series_metadata"
TITLE = "Pandas Series"
TAGS = ["pandas", "series"]
REQUIRES = ['pandas']
DISPLAY_INPUT = "pd.Series([1, 2, 3, None], name='price')"


def build():
    import pandas as pd

    return pd.Series([1, 2, 3, None], name="price")


def expected(meta):
    parts = [f"A pandas Series 'price' with {meta['metadata']['length']} values."]
    null_count = meta["metadata"].get("null_count")
    if null_count is not None:
        parts.append(f"Nulls: {null_count}.")
    dtype = meta["metadata"].get("dtype")
    if dtype:
        parts.append(f"Dtype: {dtype}.")
    stats = meta["metadata"].get("stats")
    if stats:
        parts.append(f"Stats: {stats}.")
    sample_values = meta["metadata"].get("sample_values")
    if sample_values:
        parts.append(f"Sample: [{', '.join(sample_values)}].")
    return " ".join(parts)
