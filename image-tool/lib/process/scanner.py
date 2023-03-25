import os
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
