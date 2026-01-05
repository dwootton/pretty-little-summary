ID = "short_string_url_pattern"
TITLE = "URL string"
TAGS = ["primitives", "string", "url"]
DISPLAY_INPUT = "https://example.com/foo"
EXPECTED = "A string containing a url: 'https://example.com/foo'."


def build():
    return "https://example.com/foo"
