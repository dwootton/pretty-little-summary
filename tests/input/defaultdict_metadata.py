ID = "defaultdict_metadata"
TITLE = "Defaultdict"
TAGS = ["collections", "dict"]
DISPLAY_INPUT = "defaultdict(list) grouping groceries by category"
EXPECTED = (
    "A defaultdict(default_factory=list) with 3 keys (str -> list). "
    "Keys: 'fruit', 'veg', 'grain'."
)


def build():
    from collections import defaultdict

    obj = defaultdict(list)
    for category, item in [
        ("fruit", "apple"),
        ("fruit", "pear"),
        ("veg", "carrot"),
        ("veg", "pea"),
        ("grain", "rice"),
    ]:
        obj[category].append(item)
    return obj
