#!/usr/bin/env python

import click
from cthulhu_src.actions.find_txn import run as run_cmd

"""
    Main command for find winning transaction.
"""

HELP_MAX_DEPTH = "Max depth of transaction exchange and transfer."

@click.command()
@click.pass_context
@click.option('-d', '--max_depth', type=int, default=4, help=HELP_MAX_DEPTH)
def find(ctx, max_depth):
    """
        Find winning transaction and print it.
    """
    run_cmd(ctx, max_depth)