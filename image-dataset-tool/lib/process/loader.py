from PIL import Image

from lib.process.core import Loader


class NoOpLoader(Loader):

    def load(self, name: str) -> any:
        return name


class BinaryFileLoader(Loader):

    def load(self, name: str) -> any:
        with open(name, 'rb') as fp:
            data = fp.read()
        return data


def load_pil_image(filename: str) -> Image.Image:
    return Image.open(filename, 'r')


class ImageFileLoader(Loader):

    def load(self, name: str) -> any:
        return load_pil_image(name)
