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


if __name__ == '__main__':
    config_logging()
    cli()
