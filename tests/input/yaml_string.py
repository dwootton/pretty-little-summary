ID = "yaml_string"
TITLE = "YAML string"
TAGS = ["text", "yaml"]
DISPLAY_INPUT = "name: alice\\nage: 30\\nroles:\\n  - admin\\n  - editor\\nactive: true\\n"
EXPECTED = "A valid YAML string containing keys: name, age, roles, active."


def build():
    return "name: alice\nage: 30\nroles:\n  - admin\n  - editor\nactive: true\n"
