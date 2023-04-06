import os
from typing import Callable


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


def replace_file_ext(filename: str, new_ext: str) -> str:
    prefix, _ = os.path.splitext(filename)
    if new_ext[0] != '.':
        new_ext = '.' + new_ext
    return prefix + new_ext


def read_valid_lines(filename: str) -> list[str]:
    with open(filename, 'r') as fp:
        lines = [line.strip() for line in fp.readlines()]
    return [line for line in lines if len(line) > 0 and line[0] != '#']


def write_lines(filename: str, lines: list[str], encoding: str = 'ascii'):
    data = '\n'.join(lines).encode(encoding)
    with open(filename, 'wb+') as fp:
        fp.write(data)
