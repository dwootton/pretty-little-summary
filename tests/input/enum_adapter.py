ID = "enum_adapter"
TITLE = "Enum"
TAGS = ["stdlib", "enum"]
DISPLAY_INPUT = "Color.RED"
EXPECTED = "A structured object of type enum."


def build():
    from enum import Enum

    class Color(Enum):
        RED = 1
        BLUE = 2

    return Color.RED
