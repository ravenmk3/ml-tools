import logging
import sys

from lib.cropper import ImageCropper


def setup_logging():
    logging.basicConfig(level=logging.INFO,
                        stream=sys.stdout,
                        format='[%(asctime)s][%(levelname)s][%(threadName)s] %(message)s')

if __name__ == '__main__':
    setup_logging()
    c = ImageCropper(desired_classes=[16])
    c.run()
