import io

from PIL import Image

from lib.common.geometry import max_rect_with_aspect_ratio


def image_from_bytes(buf: bytes) -> Image.Image:
    data = io.BytesIO(buf)
    return Image.open(data).convert('RGB')


def crop_with_aspect_ratio(src: Image.Image, w_scale: int, h_scale: int,
                           horizontal: str = 'center', vertical: str = 'center') -> Image.Image:
    box = max_rect_with_aspect_ratio(src.width, src.height, w_scale, h_scale, horizontal, vertical)
    return src.crop(box=box)
