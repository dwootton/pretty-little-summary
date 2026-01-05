ID = "regex_match_adapter"
TITLE = "Regex match"
TAGS = ["stdlib", "regex"]
DISPLAY_INPUT = "re.search(r'\\d+', 'abc123')"
EXPECTED = "A regex match result: matched '123' at position 3:6."


def build():
    import re

    match = re.search(r"\d+", "abc123")
    if match is None:
        raise ValueError("Expected regex match")
    return match
