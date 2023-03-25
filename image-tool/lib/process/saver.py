import os.path

from lib.process.core import Saver, Item


def _ext_of_format(format: str) -> str:
    if format == 'jpeg':
        return 'jpg'
    return format


class ImageFileSaver(Saver):

    def __init__(self, dst_dir: str, path_prefix: str = None, save_format='jpeg'):
        self.dst_dir = dst_dir
        self.path_prefix = path_prefix
        self.format = save_format.lower()
        self.dir_created = set()

    def save(self, item: Item):
        name = item.name
        if self.path_prefix:
            name = os.path.relpath(item.name, self.path_prefix)
        fullpath = os.path.join(self.dst_dir, name)
        dirpath = os.path.dirname(fullpath)
        if dirpath not in self.dir_created:
            os.makedirs(dirpath, exist_ok=True)
            self.dir_created.add(dirpath)
        path_no_ext, _ = os.path.splitext(fullpath)
        ext = _ext_of_format(self.format)
        fullpath = f'{path_no_ext}.{ext}'
        item.output.save(fullpath, format=self.format)
