import logging
from collections import defaultdict
from pprint import pprint

from cthulhu_src.services.exchange_manager import ExchangeManager
from cthulhu_src.services.processor import find_paths
from cthulhu_src.services.cross_exchange_manager import get_free_transitions

"""
    Find winning transaction.
"""


def get_order_path_history(path, adj_list):
    orders_list = []

    for i in range(len(path) - 1):
        orders_list.append(adj_list[path[i][0]][path[i + 1][0]])

    return orders_list


async def run(ctx, max_depth, exchange_list,
              start_node, start_amount, cache_dir,
              current_node=None, current_amount=None,
              cached=False, proxy=()):
    """

    :param ctx:
    :param max_depth:
    :param exchange_list:
    :param start_node:
    :param start_amount:
    :param cache_dir:
    :param current_node:
    :param current_amount:
    :param cached:
    :param proxy:
    """
    log = logging.getLogger('excthulhu')
    log.info(f'Start finding transactions with max depth {max_depth} for exchanges: {", ".join(exchange_list)}')

    log.info(f'Start loading data...')

    exchange_manager = ExchangeManager(exchange_list, proxy, cached=cached, cache_dir=cache_dir)
    try:
        pairs = await exchange_manager.fetch_prices()
    finally:
        await exchange_manager.close()

    pairs += get_free_transitions(exchange_list)

    log.info(f'Finish loading')

    log.info(f'Start prepare data...')

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

    # Get index of current node
    current_node_id = None
    if current_node:
        current_node_id = currency_list.index(current_node)

    log.info(f'Finish prepare data')

    log.info(f'Start data processing...')
    paths = find_paths(adj_list=adj_list,
                       start_node=currency_list.index(start_node),
                       start_amount=start_amount,
                       current_node=current_node_id,
                       current_amount=current_amount,
                       max_depth=max_depth)
    log.info(f'Finish data processing')

    # Sort result by profit
    paths.sort(key=lambda x: x[-1][1])

    # replace currency id with name
    result = [
        [(currency_list[node[0]], node[1]) for node in path]
        for path in paths
    ]

    for path in result:
        print(*[
            f'{node[0]} ({node[1]})'
            for node in path
        ], sep=' -> ', end='')
        print(f' = {(path[-1][1] / start_amount - 1) * 100}%')

    if ctx.obj['debug']:
        for path in paths:
            orders = get_order_path_history(path, adj_list)
            pprint(orders)
            print('=' * 80)

    log.info(f'Total count of winning cycles:{len(result)}')
