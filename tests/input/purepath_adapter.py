ID = "purepath_adapter"
TITLE = "PurePath"
TAGS = ["stdlib", "pathlib"]
DISPLAY_INPUT = "PurePath('foo/bar.txt')"
EXPECTED = "A pure path 'foo/bar.txt'."


def build():
    from pathlib import PurePath

    return PurePath("foo/bar.txt")
