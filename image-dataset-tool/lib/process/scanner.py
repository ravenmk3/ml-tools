import random

from lib.common.file import scan_image_files
from lib.process.core import Scanner


class ImageFileScanner(Scanner):

    def __init__(self, root: str):
        self.root = root

    def scan(self) -> list[str]:
        return scan_image_files(self.root)


def _read_url_file(filename: str) -> list[str]:
    with open(filename, 'r') as fp:
        lines = [line.strip() for line in fp.readlines()]
    return [line for line in lines if len(line) > 0 and line[0] != '#']


class UrlListFileScanner(Scanner):

    def __init__(self, url_file: str = 'urls.txt', shuffle: bool = False):
        self.url_file = url_file
        self.shuffle = shuffle

    def scan(self) -> list[str]:
        urls = _read_url_file(self.url_file)
        if self.shuffle:
            random.shuffle(urls)
        return urls
