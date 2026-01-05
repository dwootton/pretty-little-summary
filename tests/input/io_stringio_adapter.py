ID = "io_stringio_adapter"
TITLE = "StringIO"
TAGS = ["stdlib", "io"]
DISPLAY_INPUT = "io.StringIO('hello')"
EXPECTED = "An in-memory text buffer of 5 characters."


def build():
    import io

    return io.StringIO("hello")
