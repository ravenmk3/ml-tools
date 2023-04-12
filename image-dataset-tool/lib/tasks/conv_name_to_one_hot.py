import sys
from typing import Callable

from tqdm import tqdm

from lib.common.file import read_valid_lines, write_lines


def one_hot_encoder(all_names: list[str]) -> Callable:
    name2idx = {name: i for i, name in enumerate(all_names)}
    num_labels = len(all_names)

    def encode(names: list[str]) -> list[int]:
        one_hot = [0] * num_labels
        for name in names:
            idx = name2idx[name]
            one_hot[idx] = 1
        return one_hot

    return encode


def run_conv_name_to_one_hot(label_file: str, input_file: str, output_file: str,
                             input_sep: str = ',', output_sep: str = ','):
    """
    将每行格式从 `{file}\t{name},{name},{name}` 转换为 `{file}\t0,1,0,1,0}`

    :param label_file: 包含所有标签名称的文件
    :param input_file: 输入的列表文件
    :param output_file: 输出的列表文件
    """
    print('reading list')
    input_lines = read_valid_lines(input_file)
    print('total items:', len(input_lines))

    all_names = read_valid_lines(label_file)
    print('label names:', *all_names)
    encoder = one_hot_encoder(all_names)

    output_lines = []
    pbar = tqdm(input_lines, file=sys.stdout, desc='processing')
    for input_line in pbar:
        file, names_str = input_line.split('\t')
        names = [x.strip() for x in names_str.split(input_sep)]
        one_hot = encoder(names)
        one_hot_str = output_sep.join([str(x) for x in one_hot])
        output_lines.append(f'{file}\t{one_hot_str}')

    print('save to:', output_file)
    write_lines(output_file, output_lines)
    print('all done.')
