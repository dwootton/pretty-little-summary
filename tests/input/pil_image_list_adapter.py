ID = "pil_image_list_adapter"
TITLE = "PIL image list"
TAGS = ["pil", "image"]
REQUIRES = ['PIL']
DISPLAY_INPUT = "[Image.new('RGB', (32 + i*8, 32 + i*8), color=(...)) for i in range(5)]"
EXPECTED = (
    "A list of 5 PIL images, 32x32, 40x40, 48x48, 56x56, 64x64, mode(s): RGB."
)


def build():
    from PIL import Image

    return [
        Image.new("RGB", (32 + i * 8, 32 + i * 8), color=(i * 40 % 256, i * 60 % 256, i * 80 % 256))
        for i in range(5)
    ]
