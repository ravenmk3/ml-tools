import json
import sys
from typing import Callable

from tqdm import tqdm

from lib.common.file import read_valid_lines


def make_converter(multilabel: bool) -> Callable:
    def single_label_converter(val: str) -> int:
        return int(val.strip())

    def multi_label_converter(val: str) -> list[int]:
        return [int(x.strip()) for x in val.split(',')]

    if multilabel:
        return multi_label_converter
    return single_label_converter


def run_paddle_to_mm(label_file: str, input_file: str, output_file: str, multilabel: bool = False):
    """
    将 Paddle 标注格式转换为 OpenMMLab 标注格式
    :param label_file: 包含所有标签名称的文件
    :param input_file: 输入的列表文件
    :param output_file: 输出的列表文件
    :param multilabel: 是否多标签
    """
    print('reading list')
    input_lines = read_valid_lines(input_file)
    print('total items:', len(input_lines))

    all_names = read_valid_lines(label_file)
    print('label names:', *all_names)

    convert = make_converter(multilabel)
    output_list = []
    pbar = tqdm(input_lines, file=sys.stdout, desc='processing')
    for input_line in pbar:
        file, anno = input_line.split('\t')
        output_list.append({
            'img_path': file,
            'img_label': convert(anno),
        })

    output_data = {
        'metainfo': {
            'classes': all_names,
        },
        'data_list': output_list,
    }

    print('save to:', output_file)
    with open(output_file, 'w+') as fp:
        json.dump(output_data, fp)
    print('all done.')
