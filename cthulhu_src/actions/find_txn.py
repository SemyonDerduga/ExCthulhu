from pprint import pprint

from cthulhu_src.services.exchanger_service import ExchangerManager

"""
    Find winning transaction.
"""


async def run(ctx, max_depth):
    """

    :param ctx: click context object
    :param max_depth: int
    :return:
    """
    log = ctx.obj["logger"]
    log.info(f"Start finding transactions with max depth {max_depth}...")

    exchange_manager = ExchangerManager()
    try:
        prices = await exchange_manager.fetch_prices()
    finally:
        await exchange_manager.close()

    pprint(prices)
