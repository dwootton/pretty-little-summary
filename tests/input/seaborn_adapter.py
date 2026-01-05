ID = "seaborn_adapter"
TITLE = "Seaborn grid"
TAGS = ["seaborn", "chart"]
REQUIRES = ['seaborn', 'pandas']
DISPLAY_INPUT = "seaborn.FacetGrid(df, col='group')"


def build():
    import pandas as pd
    import seaborn

    df = pd.DataFrame({"x": [1, 2, 3], "y": [3, 4, 5], "group": ["a", "a", "b"]})
    return seaborn.FacetGrid(df, col="group")


def expected(meta):
    return f"A seaborn {meta['metadata'].get('grid_type')} with {meta['metadata'].get('axes_count')} axes."
