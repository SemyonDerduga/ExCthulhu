import click

from cthulhu_src.actions.available_io import run as run_cmd

"""
    Command for getting currencies available for input and output for exchange.
"""

@click.command()
@click.pass_context
@click.argument('exchange')
def available_io(ctx, exchange):
    """
        Getting currencies available for input and output for exchange.
    """
    run_cmd(ctx, exchange)
