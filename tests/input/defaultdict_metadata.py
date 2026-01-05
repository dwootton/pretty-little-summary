ID = "defaultdict_metadata"
TITLE = "Defaultdict"
TAGS = ["collections", "dict"]
DISPLAY_INPUT = "defaultdict(list, {'a': [1]})"
EXPECTED = "A defaultdict with 1 keys."


def build():
    from collections import defaultdict

    obj = defaultdict(list)
    obj["a"].append(1)
    return obj
