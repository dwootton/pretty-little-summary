ID = "regex_match_adapter"
TITLE = "Regex match"
TAGS = ["stdlib", "regex"]
DISPLAY_INPUT = "re.search(r'order #(\\d+) shipped on (...)', 'Your order #48213 shipped on 2026-07-30 via express')"
EXPECTED = (
    "A regex match result: matched 'order #48213 shipped on 2026-07-30' at position 5:39."
)


def build():
    import re

    match = re.search(
        r"order #(\d+) shipped on (\d{4}-\d{2}-\d{2})",
        "Your order #48213 shipped on 2026-07-30 via express",
    )
    if match is None:
        raise ValueError("Expected regex match")
    return match
