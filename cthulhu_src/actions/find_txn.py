import logging
from collections import defaultdict
from pprint import pprint

from cthulhu_src.services.exchange_manager import ExchangeManager
from cthulhu_src.services.processor import find_paths

"""
    Find winning transaction.
"""


async def run(ctx, max_depth, start, amount, exchange_list):
    """

    :param ctx: click context object
    :param max_depth: int
    :return:
    """
    log = logging.getLogger('excthulhu')
    log.info(f'Start finding transactions with max depth {max_depth} for exchanges: {", ".join(exchange_list)}')

    exchange_manager = ExchangeManager(exchange_list)
    try:
        pairs = await exchange_manager.fetch_prices()
    finally:
        await exchange_manager.close()

    adj_dict = defaultdict(list)
    for pair in pairs:
        adj_dict[pair.currency_from].append(pair)

    currency_list = list(adj_dict.keys())


    adj_list = [
        {
            currency_list.index(pair.currency_to): pair.trade_book
            for pair in adj_dict[currency_from]
        }
        for currency_from in currency_list
    ]

    result = [
        [currency_list[node] for node in path]
        for path in find_paths(adj_list, currency_list.index(start), max_depth)
    ]

    pprint(result)
