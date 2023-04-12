import logging
import sys

import click


@click.group()
def cli():
    pass


def config_logging():
    logging.basicConfig(level=logging.INFO,
                        encoding='utf-8',
                        stream=sys.stdout,
                        format='%(message)s')


@cli.command()
@click.option('--src-dir', required=True)
@click.option('--dst-dir', required=True)
@click.option('--num_workers', default=10, show_default=True)
def rename_md5(src_dir: str, dst_dir: str, num_workers: int):
    from lib.tasks import run_rename_md5 as run
    run(src_dir, dst_dir, num_workers)


@cli.command()
@click.option('--src-dir', required=True)
@click.option('--dst-dir', required=True)
@click.option('--num_workers', default=10, show_default=True)
def rename_md5_conv_webp(src_dir: str, dst_dir: str, num_workers: int):
    from lib.tasks import run_rename_md5_conv_webp as run
    run(src_dir, dst_dir, num_workers)


@cli.command()
@click.option('--dir', required=True)
def remove_empty_file(dir: str):
    from lib.tasks import run_remove_empty_file as run
    run(dir)


@cli.command()
@click.option('--src-dir', required=True)
@click.option('--dst-dir', required=True)
@click.option('--w-scale', default=4, show_default=True)
@click.option('--h-scale', default=3, show_default=True)
@click.option('--horizontal', default='center', show_default=True)
@click.option('--vertical', default='center', show_default=True)
@click.option('--num_workers', default=10, show_default=True)
def crop_with_aspect_ratio(src_dir: str, dst_dir: str, w_scale: int, h_scale: int,
                           horizontal: str, vertical: str, num_workers: int):
    from lib.tasks import run_crop_with_aspect_ratio as run
    run(src_dir, dst_dir, w_scale, h_scale, horizontal, vertical, num_workers)


@cli.command()
@click.option('--url-file', required=True)
@click.option('--save-dir', required=True)
@click.option('--shuffle', is_flag=True)
@click.option('--proxy', required=False, default=None, show_default=True)
@click.option('--num-workers', default=10, show_default=True)
def download_images(url_file: str, save_dir: str, shuffle: bool = False, proxy: str = None, num_workers: int = 10):
    from lib.tasks import run_download_images as run
    run(url_file, save_dir, shuffle, proxy, num_workers)


@cli.command()
@click.option('--dataset', required=True)
@click.option('--output-file', required=True)
def merge_split_label_file(dataset: str, output_file: str):
    from lib.tasks import run_merge_split_label_file as run
    run(dataset, output_file)


@cli.command()
@click.option('--labels', required=True)
@click.option('--input', required=True)
@click.option('--output', required=True)
@click.option('--input-sep', default=',', show_default=True)
@click.option('--output-sep', default='', show_default=True)
def named_label_to_one_hot(labels: str, input: str, output: str,
                           input_sep: str, output_sep: str):
    from lib.tasks import run_named_label_to_one_hot as run
    run(labels, input, output, input_sep, output_sep)


@cli.command()
@click.option('--labels', required=True)
@click.option('--input', required=True)
@click.option('--output', required=True)
@click.option('--multilabel', is_flag=True)
def paddle_to_mm(labels: str, input: str, output: str, multilabel: bool):
    from lib.tasks import run_paddle_to_mm as run
    run(labels, input, output, multilabel)


@cli.command()
@click.option('--data-file', required=True)
@click.option('--index-file', required=True)
@click.option('--output-file', required=True)
@click.option('--size-spec', default='z', show_default=True)
@click.option('--num-per-index', type=int, default=None, show_default=True)
def txmlimgs_filter_list(data_file: str, index_file: str, output_file: str, size_spec: str, num_per_index: int):
    from lib.tasks import run_txmlimgs_filter_list as run
    run(data_file, index_file, output_file, size_spec, num_per_index)


@cli.command()
@click.option('--data-file', required=True)
@click.option('--output-file', required=True)
@click.option('--size-spec', default='z', show_default=True)
def txmlimgs_extract_urls(data_file: str, output_file: str, size_spec: str):
    from lib.tasks import run_txmlimgs_extract_urls as run
    run(data_file, output_file, size_spec)


@cli.command()
@click.option('--data-file', required=True)
@click.option('--output-file', required=True)
def txmlimgs_make_labelmap(data_file: str, output_file: str):
    from lib.tasks import run_txmlimgs_make_labelmap as run
    run(data_file, output_file)


@cli.command()
@click.option('--data-file', required=True)
@click.option('--label-map', required=True)
@click.option('--image-dir', required=True)
@click.option('--output-dir', required=True)
@click.option('--shuffle', is_flag=True)
@click.option('--split', is_flag=True)
@click.option('--limit', default=0, show_default=True)
def txmlimgs_make_dataset(data_file: str, label_map: str, image_dir: str, output_dir: str,
                          shuffle: bool, split: bool, limit: int):
    from lib.tasks import run_txmlimgs_make_dataset as run
    run(data_file, label_map, image_dir, output_dir, shuffle, split, limit)


@cli.command()
@click.option('--data-file', required=True)
@click.option('--label-map', required=True)
@click.option('--image-dir', required=True)
@click.option('--output-dir', required=True)
@click.option('--shuffle', is_flag=True)
@click.option('--split', is_flag=True)
@click.option('--limit', default=0, show_default=True)
@click.option('--data-only', is_flag=True)
def txmlimgs_to_paddle_dataset(data_file: str, label_map: str, image_dir: str, output_dir: str,
                               shuffle: bool, split: bool, limit: int, data_only):
    from lib.tasks import run_txmlimgs_to_paddle_dataset as run
    run(data_file, label_map, image_dir, output_dir, shuffle, split, limit, data_only)


if __name__ == '__main__':
    config_logging()
    cli()
