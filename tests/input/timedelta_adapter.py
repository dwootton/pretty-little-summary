ID = "timedelta_adapter"
TITLE = "Timedelta"
TAGS = ["stdlib", "timedelta"]
DISPLAY_INPUT = "timedelta(weeks=2, days=3, hours=5, minutes=30)"
EXPECTED = "A duration of 17 days, 5 hours, 30 minutes (1488600 seconds)."


def build():
    from datetime import timedelta

    return timedelta(weeks=2, days=3, hours=5, minutes=30)
