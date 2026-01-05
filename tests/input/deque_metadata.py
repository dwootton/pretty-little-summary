ID = "deque_metadata"
TITLE = "Deque"
TAGS = ["collections", "deque"]
DISPLAY_INPUT = "deque([1, 2, 3, 4])"
EXPECTED = "A deque of 4 items."


def build():
    from collections import deque

    return deque([1, 2, 3, 4])
