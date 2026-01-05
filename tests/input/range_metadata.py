ID = "range_metadata"
TITLE = "Range"
TAGS = ["collections", "range"]
DISPLAY_INPUT = "range(0, 10, 2)"
EXPECTED = "A range from 0 to 10 with step 2."


def build():
    return range(0, 10, 2)
