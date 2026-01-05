ID = "pandas_categorical"
TITLE = "Pandas Categorical"
TAGS = ["pandas", "categorical"]
REQUIRES = ['pandas']
DISPLAY_INPUT = "pd.Categorical(['a', 'b', 'a'])"
EXPECTED = "A pandas Categorical with 2 categories."


def build():
    import pandas as pd

    return pd.Categorical(["a", "b", "a"])
