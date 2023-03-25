from PIL import Image

from lib.process.core import Loader


def load_pil_image(filename: str) -> Image.Image:
    return Image.open(filename, 'r')


class ImageFileLoader(Loader):

    def load(self, name: str) -> any:
        return load_pil_image(name)
