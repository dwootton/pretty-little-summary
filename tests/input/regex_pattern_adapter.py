ID = "regex_pattern_adapter"
TITLE = "Regex pattern"
TAGS = ["stdlib", "regex"]
DISPLAY_INPUT = "re.compile(r'^(?P<year>\\d{4})-(?P<month>\\d{2})-(?P<day>\\d{2})$')"
EXPECTED = (
    "A compiled regex pattern /^(?P<year>\\d{4})-(?P<month>\\d{2})-(?P<day>\\d{2})$/. "
    "3 capturing groups."
)


def build():
    import re

    return re.compile(r"^(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})$")
