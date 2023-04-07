import os.path
import random
import shutil
import sys
from urllib.parse import urlparse

from tqdm import tqdm

from lib.common.utils import write_lines


def _read_valid_lines(filename: str) -> list[str]:
    with open(filename, 'r') as fp:
        lines = [line.strip() for line in fp.readlines()]
    return [line for line in lines if len(line) > 0 and line[0] != '#']


def read_label_map(filename: str) -> dict[str, str]:
    lines = _read_valid_lines(filename)
    result = {}
    for line in lines:
        idx, name = line.strip().split(':')
        idx = idx.strip()
        name = name.strip()
        result[idx] = name
    return result


def parse_line(line: str) -> tuple[str, list[str]]:
    line = line.strip().split('\t')
    url = line[0]
    labels = [x.split(':')[0] for x in line[1:]]
    return url, labels


def indices_to_names(label_map: dict[str, str], indices: list[str]):
    names = []
    for idx in indices:
        name = label_map.get(idx)
        if name:
            names.append(name)
    return list(set(names))


def url_to_filename(url: str) -> str:
    u = urlparse(url)
    host = u.netloc.replace(':', '_')
    path = u.path.replace('/', '_')
    return f'{host}_{path}'


def run_txmlimgs_to_paddle_dataset(
    data_file: str, label_map_file: str, image_dir: str, output_dir: str,
    shuffle: bool = True, split: bool = True, limit: int = 0, data_only: bool = False):
    """
    从已下载的 Tencent ML Images 数据集图片文件中创建 PaddleClas 格式的数据集
    列表文件每行是 `{文件名}{制表符}{逗号分割的OneHot}` 如 `train/001.jpg  1,0,1,0,1`
    :param data_file: Tencent ML Images 的 train***_urls.txt
    :param label_map_file: 标签索引到名称的映射文件每行格式如 `123:name`, 名称是可以重复的，只有出现在这个文件的标签索引才会输出到标注。
    :param image_dir: 下载图片的目录
    :param output_dir: 数据集输出目录，复制图片和生成对应的标注文件
    """

    label_map = read_label_map(label_map_file)
    label_names = list(label_map.values())
    label_names = list(set(label_names))
    num_names = len(label_names)
    print('num label indices:', len(label_map.keys()))
    print('num label names:', num_names)
    name2idx = {n: i for i, n in enumerate(label_names)}

    subsets = {'train': 1}
    if split:
        subsets = {'train': 10, 'val': 1}

    set_names = []
    for set_name, set_weight in subsets.items():
        set_dir = os.path.join(output_dir, set_name)
        os.makedirs(set_dir, exist_ok=True)
        subsets[set_name] = (set_dir, [])
        set_names += ([set_name] * set_weight)

    label_name_file = os.path.join(output_dir, 'labels.txt')
    write_lines(label_name_file, label_names)

    print('reading lines')
    lines = _read_valid_lines(data_file)
    total = len(lines)
    num_copied = 0

    if shuffle:
        print('shuffling')
        random.shuffle(lines)

    pbar = tqdm(lines, file=sys.stdout)
    pbar.desc = 'processing'

    for line in pbar:
        url, labels = parse_line(line)
        filename = url_to_filename(url)
        filepath = os.path.join(image_dir, filename)

        if not data_only:
            if not os.path.isfile(filepath):
                continue
            size = os.path.getsize(filepath)
            if size <= 0:
                continue

        one_hot = ['0'] * num_names
        names = indices_to_names(label_map, labels)
        for name in names:
            idx = name2idx.get(name)
            one_hot[idx] = '1'
        one_hot = ','.join(one_hot)

        set_name = random.choice(set_names)
        set_dir, set_lines = subsets[set_name]
        set_lines.append(f'{filename}\t{one_hot}')
        dst_filepath = os.path.join(set_dir, filename)

        if not data_only:
            if not os.path.exists(dst_filepath):
                shutil.copy(filepath, dst_filepath)
            num_copied += 1
            if limit and num_copied >= limit:
                break

    for set_name, props in subsets.items():
        _, lines = props
        list_file = os.path.join(output_dir, f'{set_name}.txt')
        write_lines(list_file, lines)

    print(f'all done, total:{total}, copied:{num_copied}')
