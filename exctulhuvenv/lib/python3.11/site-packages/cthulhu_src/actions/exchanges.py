import ccxt
from tabulate import tabulate

"""
    Show exchanges list.
"""


def run(ctx) -> None:
    table = [[exchange] for exchange in ccxt.exchanges]
    print(tabulate(table, ["Exchanges"], tablefmt="grid"))
