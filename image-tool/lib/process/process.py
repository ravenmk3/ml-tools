import os
import shutil

from lib.process.core import Saver, WorkItem


class RenamedBinaryFileSaver(Saver):

    def __init__(self, dst_dir: str, path_prefix: str = None):
        self.dst_dir = dst_dir
        self.path_prefix = path_prefix
        self.dir_created = set()

    def save(self, item: WorkItem):
        name = item.input.name
        src_path = name
        if self.path_prefix:
            name = os.path.relpath(name, self.path_prefix)
        dst_path = os.path.join(self.dst_dir, name)
        dst_dir = os.path.dirname(dst_path)
        if dst_dir not in self.dir_created:
            os.makedirs(dst_dir, exist_ok=True)
            self.dir_created.add(dst_dir)

        _, ext = os.path.splitext(name)
        new_name = item.output + ext
        dst_path = os.path.join(dst_dir, new_name)
        shutil.copy(src_path, dst_path)
