import click
import asyncio
from cthulhu_src.actions.find_txn import run as run_cmd

"""
    Main command for find winning transaction.
"""

HELP_MAX_DEPTH = 'Max depth of transaction exchange and transfer.'
HELP_START = 'Currency and Exchange Entry Point'
HELP_AMOUNT = 'Amount of starting currency'
HELP_CACHED = 'Cache exchange data'
HELP_CURRENT_NODE = 'Currency and Exchange where you stopped'
HELP_CURRENT_AMOUNT = 'Amount of currency where you stop'


@click.command()
@click.pass_context
@click.option('-d', '--max-depth', type=int, default=4, help=HELP_MAX_DEPTH)
@click.option('-s', '--start', required=True, help=HELP_START)
@click.option('-a', '--amount', type=float, default=1.0, help=HELP_AMOUNT)
@click.option('-c', '--cached', type=bool, default=False, help=HELP_CACHED, is_flag=True)
@click.option('-e', '--exchange-list', multiple=True, default=['yobit', 'binance'])
@click.option('--current-node', required=False, help=HELP_CURRENT_NODE)
@click.option('--current-amount', required=False, type=float, help=HELP_CURRENT_AMOUNT)
def find(ctx, max_depth, start, amount, cached, exchange_list, current_node, current_amount):
    """
        Find winning transaction and print it.
    """
    asyncio.run(run_cmd(ctx, max_depth, start, amount, exchange_list, current_node, current_amount, cached))
