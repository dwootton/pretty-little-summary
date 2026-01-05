ID = "attrs_adapter"
TITLE = "Attrs class"
TAGS = ["attrs", "dataclass"]
REQUIRES = ['attr']
DISPLAY_INPUT = "Person('alice', 30)"
EXPECTED = "An attrs class Person with 2 attributes."


def build():
    import attr

    @attr.define
    class Person:
        name: str
        age: int

    return Person("alice", 30)
