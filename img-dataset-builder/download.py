import argparse
import logging
import sys

from lib.downloader import ImageDownloader
from lib.utils import read_lines


def setup_logging():
    logging.basicConfig(level=logging.INFO,
                        stream=sys.stdout,
                        format='[%(asctime)s][%(levelname)s][%(threadName)s] %(message)s')


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('--keyword-file', dest='keyword_file',
                        type=str, required=False, default='lib/dogs.txt')
    parser.add_argument('--num-per-kw', dest='num_per_kw',
                        type=int, required=False, default=200)
    return parser.parse_args()


if __name__ == '__main__':
    setup_logging()
    args = parse_args()
    keywords = read_lines(args.keyword_file)
    downloader = ImageDownloader(keywords=keywords, num_per_kw=args.num_per_kw)
    downloader.run()
