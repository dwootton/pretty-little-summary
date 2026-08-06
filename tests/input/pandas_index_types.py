ID = "pandas_index_types"
TITLE = "Pandas Index"
TAGS = ["pandas", "index"]
REQUIRES = ['pandas']
DISPLAY_INPUT = "pd.Index([f'user_{i:03d}' for i in range(15)], name='user_id')"
EXPECTED = (
    "A pandas Index 'user_id' with 15 entries, dtype str. Sample: "
    "['user_000', 'user_001', 'user_002', 'user_003', 'user_004']."
)


def build():
    import pandas as pd

    return pd.Index([f"user_{i:03d}" for i in range(15)], name="user_id")
