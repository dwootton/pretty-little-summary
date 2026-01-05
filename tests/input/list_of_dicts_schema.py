ID = "list_of_dicts_schema"
TITLE = "List of records"
TAGS = ["collections", "list", "dict"]
DISPLAY_INPUT = "[{\"a\": 1, \"b\": \"x\"}, {\"a\": 2, \"b\": \"y\"}]"
EXPECTED = "A list of 2 records with 2 consistent fields."


def build():
    return [{"a": 1, "b": "x"}, {"a": 2, "b": "y"}]
