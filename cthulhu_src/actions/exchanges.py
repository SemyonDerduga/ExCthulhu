import ccxt
from tabulate import tabulate

"""
    Show exchanges list.
"""


def run(ctx):
    table = [[exchange] for exchange in ccxt.exchanges]
    print(tabulate(table, ['Exchanges'], tablefmt="grid"))


