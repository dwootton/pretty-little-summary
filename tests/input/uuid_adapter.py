ID = "uuid_adapter"
TITLE = "UUID"
TAGS = ["stdlib", "uuid"]
DISPLAY_INPUT = "UUID('fd2559fe-4d56-4dd3-893c-2650a015551c')"
EXPECTED = "A UUID (version 4): fd2559fe-4d56-4dd3-893c-2650a015551c."


def build():
    import uuid

    return uuid.UUID("fd2559fe-4d56-4dd3-893c-2650a015551c")
