ID = "ordered_dict_metadata"
TITLE = "OrderedDict"
TAGS = ["collections", "dict", "ordered"]
DISPLAY_INPUT = "OrderedDict([('a', 1), ('b', 2)])"
EXPECTED = "A ordered_dict with 2 keys."


def build():
    from collections import OrderedDict

    return OrderedDict([("a", 1), ("b", 2)])
