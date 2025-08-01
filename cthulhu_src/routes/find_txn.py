import click
import asyncio
from cthulhu_src.actions.find_txn import run as run_cmd

"""
    Main command for find winning transaction.
"""

HELP_MAX_DEPTH = "Max depth of transaction exchange and transfer."
HELP_START = "Currency and Exchange Entry Point"
HELP_AMOUNT = "Amount of starting currency"
HELP_CACHED = "Cache exchange data"
HELP_CURRENT_NODE = "Currency and Exchange where you stopped"
HELP_CURRENT_AMOUNT = "Amount of currency where you stop"
HELP_CACHED_DIR = "Path to folder with cashed exchange data. Default: ~/.cache/cthulhu "
HELP_ALGO = "Algorithm for search: dfs or bellman-ford"
HELP_PROCESSES = "Number of worker processes for DFS"
HELP_PRUNE = "Prune ratio for DFS pruning"
HELP_BATCH = "Batch size when fetching order books"


@click.command()
@click.pass_context
@click.option("-d", "--max-depth", type=int, default=4, help=HELP_MAX_DEPTH)
@click.option("-s", "--start", required=True, help=HELP_START)
@click.option("-a", "--amount", type=float, default=1.0, help=HELP_AMOUNT)
@click.option(
    "-c", "--cached", type=bool, default=False, help=HELP_CACHED, is_flag=True
)
@click.option("--cache-dir", default="~/.cache/cthulhu", help=HELP_CACHED_DIR)
@click.option("-e", "--exchange-list", multiple=True, default=["yobit", "binance"])
@click.option("--current-node", required=False, help=HELP_CURRENT_NODE)
@click.option("--current-amount", required=False, type=float, help=HELP_CURRENT_AMOUNT)
@click.option(
    "--algorithm",
    type=click.Choice(["dfs", "bellman-ford"]),
    default="dfs",
    help=HELP_ALGO,
)
@click.option("--processes", type=int, default=None, help=HELP_PROCESSES)
@click.option("--prune-ratio", type=float, default=0.0, help=HELP_PRUNE)
@click.option("--batch-size", type=int, default=20, help=HELP_BATCH)
def find(
    ctx,
    max_depth,
    start,
    amount,
    cached,
    cache_dir,
    exchange_list,
    current_node,
    current_amount,
    algorithm,
    processes,
    prune_ratio,
    batch_size,
):
    """
    Find winning transaction and print it.
    """
    asyncio.run(
        run_cmd(
            ctx,
            max_depth,
            exchange_list,
            start,
            amount,
            cache_dir,
            current_node,
            current_amount,
            cached,
            algorithm,
            processes,
            prune_ratio,
            batch_size,
        )
    )
