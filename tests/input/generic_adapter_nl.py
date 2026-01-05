ID = "generic_adapter_nl"
TITLE = "Generic object"
TAGS = ["generic", "object"]
DISPLAY_INPUT = "Custom()"


def build():
    class Custom:
        pass

    return Custom()


def expected(meta):
    return f"An object of type {meta['object_type']}."
