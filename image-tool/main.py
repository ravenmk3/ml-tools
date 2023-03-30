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
@click.option('--epochs', default=10, show_default=True)
def rename_md5_conv_webp(src_dir: str, dst_dir: str, num_workers: int):
    from lib.tasks import rename_md5_conv_webp as run
    run(src_dir, dst_dir, num_workers)


if __name__ == '__main__':
    config_logging()
    cli()
