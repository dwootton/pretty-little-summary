ID = "list_of_ints_summary"
TITLE = "List of integers"
TAGS = ["collections", "list", "ints"]
DISPLAY_INPUT = "list(range(2, 60, 2))  # even numbers"
EXPECTED = "A list of 29 integers. Stats: range 2 to 58, mean 30, std 17."


def build():
    return list(range(2, 60, 2))
