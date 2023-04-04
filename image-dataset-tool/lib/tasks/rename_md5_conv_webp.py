import io
import os

from PIL import Image

from lib.common.utils import md5_hex
from lib.process.core import Saver, WorkItem, InputObject, MultiThreadProcessor
from lib.process.loader import BinaryFileLoader
from lib.process.scanner import ImageFileScanner


class TargetSaver(Saver):

    def __init__(self, dst_dir: str):
        self.dst_dir = dst_dir
        os.makedirs(dst_dir, exist_ok=True)

    def save(self, item: WorkItem):
        md5, data = item.output
        dst_path = os.path.join(self.dst_dir, md5 + '.webp')
        with open(dst_path, 'wb+') as fp:
            fp.write(data)


def process(input: InputObject):
    md5 = md5_hex(input.content)
    img = Image.open(io.BytesIO(input.content))
    img = img.convert('RGB')
    out = io.BytesIO()
    img.save(out, format='webp')
    bytes = out.getvalue()
    return (md5, bytes)


def run_rename_md5_conv_webp(src_dir: str, dst_dir: str, num_workers: int = 10):
    scanner = ImageFileScanner(src_dir)
    loader = BinaryFileLoader()
    saver = TargetSaver(dst_dir)
    runner = MultiThreadProcessor(scanner, loader, process, saver, num_workers)
    runner.run()
