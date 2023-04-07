import os
import sys
from abc import ABCMeta, abstractmethod

from tqdm import tqdm

from lib.common.file import read_valid_lines


class LineMatcher(metaclass=ABCMeta):

    @abstractmethod
    def match(self, line: str) -> bool:
        pass


class SimpleLineMatcher(LineMatcher):

    def __init__(self, tags: list[str]):
        self.tags = tags.copy()

    def match(self, line: str) -> bool:
        for tag in self.tags:
            if tag in line:
                return True
        return False


class CountedLineMatcher(LineMatcher):

    def __init__(self, tags: list[str], max_num: int):
        self.orig_tags = tags.copy()
        self.max_num = max_num
        self.counts = {t: 0 for t in tags}
        self.tags = set(tags.copy())

    def match(self, line: str) -> bool:
        matched = False
        tags = self.tags.copy()
        for tag in tags:
            if tag in line:
                matched = True
                self._update(tag)
        return matched

    def _update(self, tag: str):
        new_val = self.counts[tag] + 1
        self.counts[tag] = new_val
        if new_val >= self.max_num:
            self.tags.remove(tag)


def filter_lines(lines: list[str], match_tags: list[str],
                 url_size_spec: str = None, num_per_index: int = None) -> list[str]:
    output = []
    pbar = tqdm(lines, file=sys.stdout)
    pbar.desc = 'filtering lines'

    if url_size_spec:
        target_suffix = f'_{url_size_spec}.jpg'
    else:
        target_suffix = None

    if num_per_index:
        matcher = CountedLineMatcher(match_tags, num_per_index)
    else:
        matcher = SimpleLineMatcher(match_tags)

    for line in pbar:
        if len(line) < 10 or line[0] == '#':
            continue
        if not matcher.match(line):
            continue
        if target_suffix:
            line = line.replace('_o.jpg', target_suffix)
        output.append(line)
    return output


def run_txmlimgs_filter_list(data_file: str, index_file: str, output_file: str,
                             url_size_spec: str = 'z', num_per_index: int = None):
    """
    按指定标签索引过滤图片列表
    :param data_file: Tencent ML Images 的 train***_urls.txt
    :param index_file: 每行是一个 label index 的值，按这些值过滤
    :param output_file: 输出的目标文件
    :param url_size_spec: URL 尺寸规格，可以选择 o, b, c, z, n, m, t, q, s
    """
    desired_indices = read_valid_lines(index_file)
    match_tags = ['\t' + x + ':' for x in desired_indices]
    print('desired indices:', desired_indices)

    print('reading lines:', data_file)
    with open(data_file, 'rb') as fp:
        content = fp.read().decode('ascii')
    input_lines = content.split('\n')

    output_lines = filter_lines(input_lines, match_tags, url_size_spec, num_per_index)
    num_output = len(output_lines)
    print('filtered images:', num_output)

    print('saving to:', output_file)
    dir_path = os.path.dirname(output_file)
    os.makedirs(dir_path, exist_ok=True)
    with open(output_file, 'wb+') as fp:
        fp.write('\n'.join(output_lines).encode('ascii'))
    print('all done')
