import os.path
import sys

from tqdm import tqdm


def extract_urls(lines: list[str], size_spec: str = None) -> list[str]:
    urls = []
    pbar = tqdm(lines, file=sys.stdout)
    pbar.desc = 'extract urls'

    if size_spec:
        target_suffix = f'{size_spec}.jpg'
    else:
        target_suffix = None

    for line in pbar:
        if len(line) < 10 or line[0] == '#':
            continue
        url = line.split('\t')[0].strip()
        if target_suffix:
            url = url[:-5] + target_suffix
        urls.append(url)
    return urls


def run_txmlimgs_extract_urls(data_file: str, output_file: str, size_spec: str = 'z'):
    """
    从图片+标签列表文件中提取出 URL 列表

    :param data_file: Tencent ML Images 的 train***_urls.txt
    :param output_file: 输出的目标文件
    :param size_spec: URL 尺寸规格，可以选择 o, b, c, z, n, m, t, q, s
    """
    print('reading lines:', data_file)
    with open(data_file, 'rb') as fp:
        content = fp.read().decode('ascii')
    lines = content.split('\n')

    urls = extract_urls(lines, size_spec)
    num_urls = len(urls)
    print('total urls:', num_urls)

    print('saving to:', output_file)
    dir_path = os.path.dirname(output_file)
    os.makedirs(dir_path, exist_ok=True)
    with open(output_file, 'wb+') as fp:
        fp.write('\n'.join(urls).encode('ascii'))

    print('all done')
