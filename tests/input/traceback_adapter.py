ID = "traceback_adapter"
TITLE = "Traceback"
TAGS = ["stdlib", "traceback"]
DISPLAY_INPUT = "ValueError('boom') traceback"


def build():
    try:
        raise ValueError("boom")
    except ValueError as exc:
        if exc.__traceback__ is None:
            raise ValueError("Expected traceback")
        return exc.__traceback__


def expected(meta):
    frames = meta["metadata"]["frames"]
    expected_parts = [
        f"A traceback with {meta['metadata']['depth']} frames (most recent last):"
    ]
    for frame in frames:
        expected_parts.append(
            f"\u2192 {frame.get('filename')}:{frame.get('line')} in {frame.get('name')}()"
        )
    last = meta["metadata"].get("last_frame")
    if last and last.get("code"):
        expected_parts.append(f"Last frame context: '{last.get('code')}'.")
    return "\n".join(expected_parts)
