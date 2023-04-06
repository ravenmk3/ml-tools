import pandas as pd

from lib.common.utils import write_lines


def run_txmlimgs_make_labelmap(data_file: str, output_file: str):
    """
    将标签层次关系表格转换为 index 到 name 的映射文件
    :param data_file: Tencent ML Images 的 dictionary_and_semantic_hierarchy.txt
    :param output_file: 输出的目标文件
    """

    df = pd.read_csv(data_file, sep='\t')
    lines = []
    for i in range(len(df)):
        idx = df.iloc[i, 0]
        names = df.iloc[i, 3]
        label = f'({idx}) {names}'
        line = f'{idx}:{label}'
        lines.append(line)

    print('save to', output_file)
    write_lines(output_file, lines)
