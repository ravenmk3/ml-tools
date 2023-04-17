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
@click.option('--model', required=True)
@click.option('--output', required=True)
@click.option('--name-file', default=None, show_default=True)
@click.option('--num-output', default=5, show_default=True)
@click.option('--multilabel', is_flag=True)
@click.option('--check', default=True, show_default=True)
def clf_add_post_process(model: str, output: str, name_file: str, num_output: int, multilabel: bool, check: bool):
    from lib.tasks import clf_add_post_process as run
    run(model, output, name_file, num_output, multilabel, check)


if __name__ == '__main__':
    config_logging()
    cli()
