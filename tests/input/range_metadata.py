ID = "range_metadata"
TITLE = "Range"
TAGS = ["collections", "range"]
DISPLAY_INPUT = "range(0, 100, 5)"
EXPECTED = "A range from 0 to 100 with step 5."


def build():
    return range(0, 100, 5)
