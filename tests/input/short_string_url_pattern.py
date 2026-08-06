ID = "short_string_url_pattern"
TITLE = "URL string"
TAGS = ["primitives", "string", "url"]
DISPLAY_INPUT = "https://api.github.com/repos/anthropics/claude-code/issues?state=open&page=2"
EXPECTED = "A string containing a url: 'https://api.github.com/repos/anthropics/claude-code/issues?state=open&page=2'."


def build():
    return "https://api.github.com/repos/anthropics/claude-code/issues?state=open&page=2"
