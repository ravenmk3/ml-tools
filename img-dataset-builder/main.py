import os.path

import lib
from lib.downloader import ImageDownloader
from lib.utils import read_lines


if __name__ == '__main__':
    dog_names = read_lines(os.path.join(lib.LIB_PATH, 'dogs.txt'))
    dl = ImageDownloader(keywords=dog_names, num_per_kw=200)
    dl.run()
