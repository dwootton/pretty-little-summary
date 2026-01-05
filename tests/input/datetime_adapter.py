ID = "datetime_adapter"
TITLE = "Datetime"
TAGS = ["stdlib", "datetime"]
DISPLAY_INPUT = "datetime(2024, 1, 1, 12, 0, 0)"
EXPECTED = "A datetime: 2024-01-01T12:00:00. Timezone: naive. Monday."


def build():
    from datetime import datetime

    return datetime(2024, 1, 1, 12, 0, 0)
