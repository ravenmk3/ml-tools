import os.path
import shutil
import sys
from urllib.parse import urlparse

from tqdm import tqdm


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
    return names


def url_to_filename(url: str) -> str:
    u = urlparse(url)
    host = u.netloc.replace(':', '_')
    path = u.path.replace('/', '_')
    return f'{host}_{path}'


def label_filename_for(filename: str) -> str:
    name, ext = os.path.splitext(filename)
    return name + '.txt'


def write_label_file(labels: list[str], filename: str):
    txt = '\n'.join(labels)
    with open(filename, 'wb+') as fp:
        fp.write(txt.encode('utf-8'))


def run_txmlimgs_make_dataset(data_file: str, label_map_file: str, image_dir: str, output_dir: str):
    """
    从已下载的 Tencent ML Images 数据集图片文件中创建数据集
    :param data_file: Tencent ML Images 的 train***_urls.txt
    :param label_map_file: 标签索引到名称的映射文件每行格式如 `123:name`
    :param image_dir: 下载图片的目录
    :param output_dir: 数据集输出目录，复制图片和生成对应的标签文件
    """
    label_map = read_label_map(label_map_file)
    print('num labels:', len(label_map.keys()))
    lines = _read_valid_lines(data_file)
    total = len(lines)
    num_copied = 0
    pbar = tqdm(lines, file=sys.stdout)
    pbar.desc = 'processing'
    os.makedirs(output_dir, exist_ok=True)

    for line in pbar:
        url, labels = parse_line(line)
        label_names = indices_to_names(label_map, labels)
        filename = url_to_filename(url)
        filepath = os.path.join(image_dir, filename)
        if not os.path.isfile(filepath):
            continue
        size = os.path.getsize(filepath)
        if size <= 0:
            continue

        lbl_filename = label_filename_for(filename)
        dst_filepath = os.path.join(output_dir, filename)
        dst_lbl_path = os.path.join(output_dir, lbl_filename)

        shutil.copy(filepath, dst_filepath)
        write_label_file(label_names, dst_lbl_path)
        num_copied += 1

    print(f'all done, total:{total}, copied:{num_copied}')
