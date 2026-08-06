ID = "xml_string"
TITLE = "XML string"
TAGS = ["text", "xml"]
DISPLAY_INPUT = "<catalog><book id='1'><title>Dune</title>...</book>...</catalog>"
EXPECTED = "A valid XML document with root <catalog>."


def build():
    return (
        '<?xml version="1.0"?>\n'
        "<catalog>\n"
        '  <book id="1"><title>Dune</title><author>Herbert</author></book>\n'
        '  <book id="2"><title>Foundation</title><author>Asimov</author></book>\n'
        "</catalog>"
    )
