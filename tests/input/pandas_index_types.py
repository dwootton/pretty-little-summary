ID = "pandas_index_types"
TITLE = "Pandas Index"
TAGS = ["pandas", "index"]
REQUIRES = ['pandas']
DISPLAY_INPUT = "pd.Index([1, 2, 3], name='ids')"
EXPECTED = "A pandas Index with 3 entries."


def build():
    import pandas as pd

    return pd.Index([1, 2, 3], name="ids")
