ID = "pandas_categorical"
TITLE = "Pandas Categorical"
TAGS = ["pandas", "categorical"]
REQUIRES = ['pandas']
DISPLAY_INPUT = "pd.Categorical(['gold']*2 + ['silver']*5 + ['bronze']*9 + ['unranked']*20, ...)"
EXPECTED = (
    "A pandas Categorical with 4 ordered categories ('unranked', 'bronze', "
    "'silver', 'gold') over 36 values. Counts: unranked: 20, bronze: 9, "
    "silver: 5, gold: 2."
)


def build():
    import pandas as pd

    return pd.Categorical(
        ["gold"] * 2 + ["silver"] * 5 + ["bronze"] * 9 + ["unranked"] * 20,
        categories=["unranked", "bronze", "silver", "gold"],
        ordered=True,
    )
