from PIL import Image


def load_pil_image(filename: str) -> Image.Image:
    return Image.open(filename, 'r')
