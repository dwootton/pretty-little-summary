ID = "io_bytesio_adapter"
TITLE = "BytesIO"
TAGS = ["stdlib", "io"]
DISPLAY_INPUT = "io.BytesIO(b'RIFF' + bytes(range(60)))"
EXPECTED = "An in-memory bytes buffer of 64 bytes."


def build():
    import io

    return io.BytesIO(b"RIFF" + bytes(range(60)))
