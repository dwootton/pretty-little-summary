ID = "tuple_metadata"
TITLE = "Tuple"
TAGS = ["collections", "tuple"]
DISPLAY_INPUT = "(1969, 'Apollo 11', 3.5, True, None)"
EXPECTED = (
    "A tuple of 5 elements (int, str, float, bool, NoneType): "
    "(1969, 'Apollo 11', 3.5, True, None)."
)


def build():
    return (1969, "Apollo 11", 3.5, True, None)
