import click

from cthulhu_src.actions.config import run as run_cmd

"""
    Command for find winning transaction with start settings from config file.
"""


@click.command()
@click.pass_context
@click.argument("config", type=click.Path(exists=True))
def config(ctx, config):
    """
    Find winning transaction and print it with start settings from config file.
    """
    run_cmd(ctx, config)
