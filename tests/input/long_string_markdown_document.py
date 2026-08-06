ID = "long_string_markdown_document"
TITLE = "Markdown document"
TAGS = ["primitives", "string", "markdown"]
DISPLAY_INPUT = "# Release Notes\n\n## v2.3.0\n\n- Added streaming support...\n... (repeated)"
EXPECTED = "A markdown document string (1974 chars, 85 lines, 252 words)."


def build():
    text = (
        "# Release Notes\n\n"
        "## v2.3.0\n\n"
        "- Added streaming support for large uploads\n"
        "- Fixed a race condition in the connection pool\n"
        "- Deprecated the legacy `auth_token` parameter\n\n"
        "```python\n"
        'client = Client(api_key="sk-...")\n'
        "response = client.upload(path, stream=True)\n"
        "```\n\n"
        "See the [migration guide](https://example.com/migrate) for details.\n"
    )
    return text * 6
