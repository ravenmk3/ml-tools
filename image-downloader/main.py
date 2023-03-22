import os

import click

from lib.common import config_logging


@click.group()
def cli():
    pass


@cli.command()
@click.option('--keyword', required=True)
@click.option('--output', default='./images/baidu', show_default=True)
@click.option('--limit', default=1000, show_default=True)
def baidu_image(keyword: str, output: str, limit: int):
    from lib.baiduimg import BaiduImageClient
    from lib.download import ImageDownloader

    os.makedirs(output, exist_ok=True)
    client = BaiduImageClient()
    dl = ImageDownloader(client)
    dl.run(keyword, output, 'bd_', limit)


if __name__ == '__main__':
    config_logging()
    cli()
