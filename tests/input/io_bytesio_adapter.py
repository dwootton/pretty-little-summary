ID = "io_bytesio_adapter"
TITLE = "BytesIO"
TAGS = ["stdlib", "io"]
DISPLAY_INPUT = "io.BytesIO(b'hello')"
EXPECTED = "An in-memory bytes buffer of 5 bytes."


def build():
    import io

    return io.BytesIO(b"hello")
