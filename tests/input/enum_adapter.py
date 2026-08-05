ID = "enum_adapter"
TITLE = "Enum"
TAGS = ["stdlib", "enum"]
DISPLAY_INPUT = "Color.RED"
EXPECTED = "An enum Color: RED (one of 2 members: RED, BLUE)."


def build():
    from enum import Enum

    class Color(Enum):
        RED = 1
        BLUE = 2

    return Color.RED
