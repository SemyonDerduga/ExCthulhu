import click
import asyncio
from cthulhu_src.actions.find_txn import run as run_cmd

"""
    Main command for find winning transaction.
"""

HELP_MAX_DEPTH = "Максимальная глубина поиска транзакций (по умолчанию: 4)"
HELP_START = "Точка входа в формате 'биржа_валюта' (например: binance_BTC)"
HELP_AMOUNT = "Количество исходной валюты (по умолчанию: 1.0)"
HELP_CACHED = "Использовать кешированные данные бирж"
HELP_CURRENT_NODE = "Продолжить поиск с промежуточной точки в формате 'биржа_валюта'"
HELP_CURRENT_AMOUNT = "Количество валюты в промежуточной точке"
HELP_CACHED_DIR = "Путь к папке с кешированными данными (по умолчанию: ~/.cache/cthulhu)"
HELP_ALGO = "Алгоритм поиска: dfs (поиск в глубину) или bellman-ford"
HELP_PROCESSES = "Количество рабочих процессов для DFS"
HELP_PRUNE = "Коэффициент отсечения нерентабельных веток (0.0-1.0)"
HELP_BATCH = "Размер батча при загрузке книг ордеров"


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
) -> None:
    """
    Найти прибыльные циклы арбитража между биржами.
    
    Эта команда ищет возможности для арбитража - ситуации, когда можно
    купить валюту на одной бирже и продать на другой с прибылью.
    
    Алгоритм ищет циклы обмена валют между биржами, которые могут
    принести прибыль после комиссий.
    
    Примеры:
        python -m cthulhu_src.main find -s binance_BTC -a 0.001
        python -m cthulhu_src.main find -s yobit_ETH -e binance -e hollaex
        python -m cthulhu_src.main find -s binance_BTC --algorithm bellman-ford
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
