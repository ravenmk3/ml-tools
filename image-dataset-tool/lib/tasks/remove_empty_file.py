import os
import sys

from tqdm import tqdm


def run_remove_empty_file(input_dir: str):
    print('scanning')
    files = os.listdir(input_dir)
    removed = 0
    pbar = tqdm(files, file=sys.stdout)
    pbar.desc = 'processing'
    for file in pbar:
        filepath = os.path.join(input_dir, file)
        size = os.path.getsize(filepath)
        if size <= 0:
            os.unlink(filepath)
            removed += 1
    print(f'all done, removed: {removed}')
