ID = "long_string_markdown_document"
TITLE = "Markdown document"
TAGS = ["primitives", "string", "markdown"]
DISPLAY_INPUT = "# Title\n\nThis is a paragraph.\n\n```python\nprint('hi')\n```\n... (repeated)"
EXPECTED = "A markdown document string (570 chars)."


def build():
    text = "# Title\n\nThis is a paragraph.\n\n```python\nprint('hi')\n```\n"
    return text * 10
