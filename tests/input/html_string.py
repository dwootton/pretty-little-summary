ID = "html_string"
TITLE = "HTML string"
TAGS = ["text", "html"]
DISPLAY_INPUT = "<html><body><div>hello</div></body></html>"
EXPECTED = "An HTML document or fragment."


def build():
    return "<html><body><div>hello</div></body></html>"
