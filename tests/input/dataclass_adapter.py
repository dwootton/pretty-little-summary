ID = "dataclass_adapter"
TITLE = "Dataclass"
TAGS = ["stdlib", "dataclass"]
DISPLAY_INPUT = "Point(x=1, y=2)"
EXPECTED = "A structured object of type dataclass."


def build():
    from dataclasses import dataclass

    @dataclass
    class Point:
        x: int
        y: int

    return Point(1, 2)
