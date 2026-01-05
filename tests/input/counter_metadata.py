ID = "counter_metadata"
TITLE = "Counter"
TAGS = ["collections", "counter"]
DISPLAY_INPUT = "Counter({'a': 2, 'b': 1})"
EXPECTED = "A Counter with 2 unique elements totaling 3 observations."


def build():
    from collections import Counter

    return Counter({"a": 2, "b": 1})
