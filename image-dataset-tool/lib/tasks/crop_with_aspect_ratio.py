import io

from lib.common.imgproc import image_from_bytes, crop_with_aspect_ratio
from lib.process.core import InputObject, MultiThreadProcessor
from lib.process.loader import BinaryFileLoader
from lib.process.saver import BinaryFileSaver
from lib.process.scanner import ImageFileScanner


def make_processor(w_scale: int, h_scale: int, horizontal: str, vertical: str):
    def process(input: InputObject):
        img = image_from_bytes(input.content)
        img = crop_with_aspect_ratio(img, w_scale, h_scale, horizontal, vertical)
        out = io.BytesIO()
        img.save(out, format='webp')
        return out.getvalue()

    return process


def run_crop_with_aspect_ratio(src_dir: str, dst_dir: str, w_scale: int, h_scale: int,
                               horizontal: str, vertical: str, num_workers: int = 10):
    scanner = ImageFileScanner(src_dir)
    loader = BinaryFileLoader()
    saver = BinaryFileSaver(dst_dir, src_dir, file_ext='webp')
    process = make_processor(w_scale, h_scale, horizontal, vertical)
    runner = MultiThreadProcessor(scanner, loader, process, saver, num_workers)
    runner.run()
