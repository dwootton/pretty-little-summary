ID = "enum_adapter"
TITLE = "Enum"
TAGS = ["stdlib", "enum"]
DISPLAY_INPUT = "Status.ACTIVE"
EXPECTED = "An enum Status: ACTIVE (one of 4 members: PENDING, ACTIVE, SUSPENDED, CLOSED)."


def build():
    from enum import Enum

    class Status(Enum):
        PENDING = 1
        ACTIVE = 2
        SUSPENDED = 3
        CLOSED = 4

    return Status.ACTIVE
