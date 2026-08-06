ID = "bytes_signature"
TITLE = "PNG bytes"
TAGS = ["primitives", "bytes"]
DISPLAY_INPUT = "PNG signature + IHDR chunk for a 1920x1080 image"
EXPECTED = "A bytes object containing png data (69 bytes)."


def build():
    signature = b"\x89PNG\r\n\x1a\n"
    ihdr_data = (1920).to_bytes(4, "big") + (1080).to_bytes(4, "big") + b"\x08\x06\x00\x00\x00"
    ihdr_chunk = len(ihdr_data).to_bytes(4, "big") + b"IHDR" + ihdr_data
    return signature + ihdr_chunk + bytes(range(40))
