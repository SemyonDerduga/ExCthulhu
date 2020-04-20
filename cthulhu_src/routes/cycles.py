import click

from cthulhu_src.actions.cycles import run as run_cmd

"""
    Command show exchanges list.
"""

@click.command()
@click.pass_context
def cycles(ctx):
    """
        Find simple cycles.
    """
    run_cmd(ctx)
