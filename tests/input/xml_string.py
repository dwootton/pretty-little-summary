ID = "xml_string"
TITLE = "XML string"
TAGS = ["text", "xml"]
DISPLAY_INPUT = "<root><child>value</child></root>"
EXPECTED = "A valid XML document with root <root>."


def build():
    return "<root><child>value</child></root>"
