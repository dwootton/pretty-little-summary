ID = "regex_pattern_adapter"
TITLE = "Regex pattern"
TAGS = ["stdlib", "regex"]
DISPLAY_INPUT = "re.compile(r'\\w+')"
EXPECTED = "A compiled regex pattern /\\\\w+/."


def build():
    import re

    return re.compile(r"\\w+")
