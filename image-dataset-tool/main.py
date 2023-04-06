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
@click.option('--shuffle', default=False, show_default=True)
@click.option('--proxy', required=False, default=None, show_default=True)
@click.option('--num-workers', default=10, show_default=True)
def download_images(url_file: str, save_dir: str, shuffle: bool = False, proxy: str = None, num_workers: int = 10):
    from lib.tasks import run_download_images as run
    run(url_file, save_dir, shuffle, proxy, num_workers)


@cli.command()
@click.option('--data-file', required=True)
@click.option('--index-file', required=True)
@click.option('--output-file', required=True)
@click.option('--size-spec', default='z', show_default=True)
def txmlimgs_filter_list(data_file: str, index_file: str, output_file: str, size_spec: str):
    from lib.tasks import run_txmlimgs_filter_list as run
    run(data_file, index_file, output_file, size_spec)


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
@click.option('--shuffle', default=False, show_default=True)
@click.option('--split', default=False, show_default=True)
@click.option('--limit', default=-1, show_default=True)
def txmlimgs_make_dataset(data_file: str, label_map: str, image_dir: str, output_dir: str,
                          shuffle: bool, split: bool, limit: int):
    from lib.tasks import run_txmlimgs_make_dataset as run
    run(data_file, label_map, image_dir, output_dir, shuffle, split, limit)


@cli.command()
@click.option('--data-file', required=True)
@click.option('--label-map', required=True)
@click.option('--image-dir', required=True)
@click.option('--output-dir', required=True)
@click.option('--shuffle', default=False, show_default=True)
@click.option('--split', default=False, show_default=True)
@click.option('--limit', default=-1, show_default=True)
def txmlimgs_to_paddle_dataset(data_file: str, label_map: str, image_dir: str, output_dir: str,
                               shuffle: bool, split: bool, limit: int):
    from lib.tasks import run_txmlimgs_to_paddle_dataset as run
    run(data_file, label_map, image_dir, output_dir, shuffle, split, limit)


if __name__ == '__main__':
    config_logging()
    cli()
