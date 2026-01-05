ID = "pil_image_adapter"
TITLE = "PIL image"
TAGS = ["pil", "image"]
REQUIRES = ['PIL']
DISPLAY_INPUT = "Image.new('RGB', (64, 32))"
EXPECTED = "A PIL image 64x32 in RGB mode."


def build():
    from PIL import Image

    return Image.new("RGB", (64, 32))
