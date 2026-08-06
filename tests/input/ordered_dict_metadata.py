ID = "ordered_dict_metadata"
TITLE = "OrderedDict"
TAGS = ["collections", "dict", "ordered"]
DISPLAY_INPUT = "OrderedDict of letter -> square, insertion order preserved"
EXPECTED = "An OrderedDict with 6 keys (str -> int). Stats: range 0 to 25, mean 9.2, std 9.7."


def build():
    from collections import OrderedDict

    return OrderedDict((chr(97 + i), i * i) for i in range(6))
