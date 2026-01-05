ID = "pil_image_list_adapter"
TITLE = "PIL image list"
TAGS = ["pil", "image"]
REQUIRES = ['PIL']
DISPLAY_INPUT = "[Image.new('RGB', (32, 32)) for _ in range(3)]"
EXPECTED = "A list of 3 PIL images."


def build():
    from PIL import Image

    return [Image.new("RGB", (32, 32)) for _ in range(3)]
