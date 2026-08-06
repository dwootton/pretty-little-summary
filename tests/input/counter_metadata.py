ID = "counter_metadata"
TITLE = "Counter"
TAGS = ["collections", "counter"]
DISPLAY_INPUT = "Counter(letters of 'mississippiriverbasin')"
EXPECTED = (
    "A Counter with 10 unique elements totaling 21 observations. "
    "Most common: 'i': 6, 's': 5, 'p': 2."
)


def build():
    from collections import Counter

    return Counter("mississippi river basin".replace(" ", ""))
