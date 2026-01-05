ID = "pathlib_adapter"
TITLE = "Pathlib Path"
TAGS = ["stdlib", "pathlib"]
DISPLAY_INPUT = "Path(tmp_path / 'sample.txt')"
REQUIRES_TMP_PATH = True


def build(tmp_path=None):
    from pathlib import Path

    if tmp_path is None:
        raise ValueError("tmp_path is required")
    target = tmp_path / "sample.txt"
    target.write_text("hello")
    return Path(target)


def expected(meta):
    return f"A path '{meta['metadata']['path']}' pointing to an existing file (5.0 B)."
