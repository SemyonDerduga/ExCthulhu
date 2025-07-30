import click

from cthulhu_src.actions.exchanges import run as run_cmd

"""
    Command show exchanges list.
"""


@click.command()
@click.pass_context
def exchanges(ctx):
    """
    Show exchanges list.
    """
    run_cmd(ctx)
