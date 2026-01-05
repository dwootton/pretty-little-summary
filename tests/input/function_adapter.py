ID = "function_adapter"
TITLE = "Function"
TAGS = ["stdlib", "callable"]
DISPLAY_INPUT = "def sample_fn(x): return x + 1"
EXPECTED = "A callable function named sample_fn."


def build():
    def sample_fn(x: int) -> int:
        return x + 1

    return sample_fn
