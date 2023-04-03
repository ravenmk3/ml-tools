import sys

from tqdm import tqdm


def _read_valid_lines(filename: str) -> list[str]:
    with open(filename, 'r') as fp:
        lines = [line.strip() for line in fp.readlines()]
    return [line for line in lines if len(line) > 0 and line[0] != '#']


def is_line_matched(line: str, match_tags: list[str]) -> bool:
    for tag in match_tags:
        if tag in line:
            return True
    return False


def filter_lines(lines: list[str], match_tags: list[str], url_size_spec: str = None) -> list[str]:
    output = []
    pbar = tqdm(lines, file=sys.stdout)
    pbar.desc = 'filtering lines'

    if url_size_spec:
        target_suffix = f'{url_size_spec}.jpg'
    else:
        target_suffix = None

    for line in pbar:
        if len(line) < 10 or line[0] == '#':
            continue
        if not is_line_matched(line, match_tags):
            continue
        if target_suffix:
            line = line[:-5] + target_suffix
        output.append(line)
    return output


def run_txmlimgs_filter_list(data_file: str, index_file: str, output_file: str, url_size_spec: str = 'z'):
    """
    按指定标签索引过滤图片列表
    :param data_file: Tencent ML Images 的 train***_urls.txt
    :param index_file: 每行是一个 label index 的值，按这些值过滤
    :param output_file: 输出的目标文件
    :param url_size_spec: URL 尺寸规格，可以选择 o, b, c, z, n, m, t, q, s
    """
    desired_indices = _read_valid_lines(index_file)
    match_tags = ['\t' + x + ':' for x in desired_indices]
    print('desired indices:', desired_indices)

    print('reading lines:', data_file)
    with open(data_file, 'rb') as fp:
        content = fp.read().decode('ascii')
    input_lines = content.split('\n')

    output_lines = filter_lines(input_lines, match_tags, url_size_spec)
    num_output = len(output_lines)
    print('filtered images:', num_output)

    print('saving to:', output_file)
    with open(output_file, 'wb+') as fp:
        fp.write('\n'.join(output_lines).encode('ascii'))
    print('all done')
