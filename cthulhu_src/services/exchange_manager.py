import asyncio
import itertools
from typing import Tuple

from cthulhu_src.services.exchanges import *

exchanges_instances = {
    'binance': Binance,
    'dsx': Dsx,
    'exmo': Exmo,
    'hollaex': Hollaex,
    'oceanex': Oceanex,
    'poloniex': Poloniex,
    'tidex': Tidex,
    'upbit': Upbit,
    'yobit': Yobit,
}


def get_exchange_by_name(exchange_name):
    if exchange_name in exchanges_instances:
        return exchanges_instances[exchange_name]()
    else:
        return GenericExchange(exchange_name)


class ExchangeManager:
    def __init__(self, exchanges: [str]):
        self._exchanges: [BaseExchange] = [
            get_exchange_by_name(name)
            for name in exchanges
        ]

    async def close(self):
        await asyncio.gather(*[
            exchanger.close()
            for exchanger in self._exchanges
        ])

    async def fetch_prices(self) -> [Tuple[str, str, float]]:
        results = await asyncio.gather(*[
            exchanger.fetch_prices()
            for exchanger in self._exchanges
        ])

        prices = list(itertools.chain(*results))
        return prices
