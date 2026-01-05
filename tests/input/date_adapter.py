ID = "date_adapter"
TITLE = "Date"
TAGS = ["stdlib", "date"]
DISPLAY_INPUT = "date(2024, 1, 1)"
EXPECTED = "A date: 2024-01-01. Monday."


def build():
    from datetime import date

    return date(2024, 1, 1)
