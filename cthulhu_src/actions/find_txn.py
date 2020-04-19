from pprint import pprint

from cthulhu_src.services.exchange_manager import ExchangeManager

"""
    Find winning transaction.
"""


async def run(ctx, max_depth, exchange_list):
    """

    :param ctx: click context object
    :param max_depth: int
    :return:
    """
    log = ctx.obj['logger']
    log.info(f'Start finding transactions with max depth {max_depth} for exchanges: {", ".join(exchange_list)}')

    exchange_manager = ExchangeManager(exchange_list)
    try:
        prices = await exchange_manager.fetch_prices()
        pprint(prices)
    finally:
        await exchange_manager.close()


