ID = "time_adapter"
TITLE = "Time"
TAGS = ["stdlib", "time"]
DISPLAY_INPUT = "time(14, 30, 0)"
EXPECTED = "A time: 14:30:00. Timezone: naive."


def build():
    from datetime import time

    return time(14, 30, 0)
