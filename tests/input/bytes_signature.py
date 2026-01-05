ID = "bytes_signature"
TITLE = "PNG bytes"
TAGS = ["primitives", "bytes"]
DISPLAY_INPUT = "b'\\x89PNG\\r\\n\\x1a\\n' + b'\\x00' * 20"
EXPECTED = "A bytes object containing png data (28 bytes)."


def build():
    return b"\x89PNG\r\n\x1a\n" + b"\x00" * 20
