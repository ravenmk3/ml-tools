import os
import shutil

from lib.common.utils import md5_hex
from lib.process.core import Saver, WorkItem, InputObject, MultiThreadProcessor
from lib.process.loader import BinaryFileLoader
from lib.process.scanner import ImageFileScanner


class TargetSaver(Saver):

    def __init__(self, dst_dir: str):
        self.dst_dir = dst_dir
        os.makedirs(dst_dir, exist_ok=True)

    def save(self, item: WorkItem):
        _, ext = os.path.splitext(item.input.name)
        md5 = item.output
        dst_path = os.path.join(self.dst_dir, md5 + ext)
        shutil.copy(item.input.name, dst_path)


def process(input: InputObject):
    return md5_hex(input.content)


def rename_md5(src_dir: str, dst_dir: str, num_workers: int = 10):
    scanner = ImageFileScanner(src_dir)
    loader = BinaryFileLoader()
    saver = TargetSaver(dst_dir)
    runner = MultiThreadProcessor(scanner, loader, process, saver, num_workers)
    runner.run()
