import os.path
import sys

from tqdm import tqdm

from lib.common.file import scan_image_files, replace_file_ext, read_valid_lines, write_lines


def run_merge_split_label_file(dataset_dir: str, output_file: str):
    """
    将所有图片对应的标签文件合并为一个列表
    """
    print('scanning image files')
    img_files = scan_image_files(dataset_dir)
    print('image files found:', len(img_files))

    output = []
    no_label_files = []
    pbar = tqdm(img_files, file=sys.stdout, desc='processing')
    for img_file in pbar:
        img_relpath = os.path.relpath(img_file, dataset_dir)
        lbl_path = replace_file_ext(img_file, '.txt')
        if not os.path.isfile(lbl_path):
            no_label_files.append(img_relpath)
            continue

        labels = read_valid_lines(lbl_path)
        lbl_str = ','.join(labels)
        output.append(f'{img_relpath}\t{lbl_str}')

    print('save merged labels to:', output_file)
    write_lines(output_file, output)
    print('all done.')
