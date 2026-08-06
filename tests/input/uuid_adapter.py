ID = "uuid_adapter"
TITLE = "UUID"
TAGS = ["stdlib", "uuid"]
DISPLAY_INPUT = "uuid.uuid5(uuid.NAMESPACE_DNS, 'anthropic.com')"
EXPECTED = "A UUID (version 5): 2a83bb89-17ca-5414-803b-3a2aa958cb48."


def build():
    import uuid

    return uuid.uuid5(uuid.NAMESPACE_DNS, "anthropic.com")
