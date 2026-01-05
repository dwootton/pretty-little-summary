ID = "json_string"
TITLE = "JSON string"
TAGS = ["text", "json"]
DISPLAY_INPUT = "{\"name\": \"alice\", \"age\": 30}"
EXPECTED = "A valid JSON string containing an object with keys: name, age."


def build():
    return '{"name": "alice", "age": 30}'
