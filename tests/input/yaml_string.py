ID = "yaml_string"
TITLE = "YAML string"
TAGS = ["text", "yaml"]
DISPLAY_INPUT = "name: alice\\nage: 30\\n"
EXPECTED = "A valid YAML string containing keys: name, age."


def build():
    return "name: alice\nage: 30\n"
