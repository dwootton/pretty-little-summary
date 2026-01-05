ID = "altair_adapter"
TITLE = "Altair chart"
TAGS = ["altair", "chart"]
REQUIRES = ['altair', 'pandas']
DISPLAY_INPUT = "altair.Chart(df).mark_line().encode(x='x', y='y')"
EXPECTED = "An Altair chart with mark '{'type': 'line'}'."


def build():
    import altair
    import pandas as pd

    return altair.Chart(pd.DataFrame({"x": [1, 2], "y": [3, 4]})).mark_line().encode(
        x="x", y="y"
    )
