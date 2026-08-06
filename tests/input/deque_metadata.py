ID = "deque_metadata"
TITLE = "Deque"
TAGS = ["collections", "deque"]
DISPLAY_INPUT = "deque(range(1, 30, 2))  # sliding window of odd numbers"
EXPECTED = "A deque of 15 items, front: [1, 3, 5], back: [25, 27, 29]."


def build():
    from collections import deque

    return deque(range(1, 30, 2))
