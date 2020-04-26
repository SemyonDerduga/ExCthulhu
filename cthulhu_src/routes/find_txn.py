import click
import asyncio
from cthulhu_src.actions.find_txn import run as run_cmd

"""
    Main command for find winning transaction.
"""

HELP_MAX_DEPTH = 'Max depth of transaction exchange and transfer.'
HELP_START = 'Currency and Exchange Entry Point'
HELP_ = 'Amount of starting currency'


@click.command()
@click.pass_context
@click.option('-d', '--max_depth', type=int, default=4, help=HELP_MAX_DEPTH)
@click.option('-s', '--start', required=True, help=HELP_START)
@click.option('-a', '--amount', type=float, default=1.0, help=HELP_START)
@click.option('-e', '--exchange_list', multiple=True, default=['yobit', 'binance'])
def find(ctx, max_depth, start, amount, exchange_list):
    """
        Find winning transaction and print it.
    """
    asyncio.run(run_cmd(ctx, max_depth, start, amount, exchange_list))
