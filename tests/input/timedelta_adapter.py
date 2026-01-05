ID = "timedelta_adapter"
TITLE = "Timedelta"
TAGS = ["stdlib", "timedelta"]
DISPLAY_INPUT = "timedelta(days=2, hours=3)"
EXPECTED = "A duration of 2 days (183600 seconds)."


def build():
    from datetime import timedelta

    return timedelta(days=2, hours=3)
