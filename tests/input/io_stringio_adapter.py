ID = "io_stringio_adapter"
TITLE = "StringIO"
TAGS = ["stdlib", "io"]
DISPLAY_INPUT = "io.StringIO('INFO startup complete\\nWARN cache miss...')"
EXPECTED = "An in-memory text buffer of 87 characters."


def build():
    import io

    log = (
        "INFO startup complete\n"
        "WARN cache miss on key user:1234\n"
        "ERROR retrying connection to db\n"
    )
    return io.StringIO(log)
