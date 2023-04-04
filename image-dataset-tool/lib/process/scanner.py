import os
import random
from typing import Callable

from lib.process.core import Scanner


IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.bmp', '.webp']


def _noop_filter(_: str) -> bool:
    return True


def scan_files(dir_path: str, filter: Callable = None) -> list[str]:
    result = []
    if not filter:
        filter = _noop_filter
    for root, dirs, files in os.walk(dir_path):
        for file in files:
            filepath = os.path.join(root, file)
            if filter(filepath):
                result.append(filepath)
    return result


def is_image_file(filename: str) -> bool:
    filename = filename.lower()
    for ext in IMAGE_EXTENSIONS:
        if filename.endswith(ext):
            return True
    return False


def scan_image_files(dir_path: str) -> list[str]:
    result = []
    for root, dirs, files in os.walk(dir_path):
        for file in files:
            if not is_image_file(file):
                continue
            result.append(os.path.join(root, file))
    return result


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
