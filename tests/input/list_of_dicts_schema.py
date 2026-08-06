ID = "list_of_dicts_schema"
TITLE = "List of records"
TAGS = ["collections", "list", "dict"]
DISPLAY_INPUT = "[{'id': 1, 'city': 'Austin', 'population': 964254}, ...]"
EXPECTED = "A list of 6 records with 3 consistent fields."


def build():
    return [
        {"id": 1, "city": "Austin", "population": 964254},
        {"id": 2, "city": "Denver", "population": 715522},
        {"id": 3, "city": "Seattle", "population": 737015},
        {"id": 4, "city": "Boston", "population": 654776},
        {"id": 5, "city": "Miami", "population": 442241},
        {"id": 6, "city": "Portland", "population": 652503},
    ]
