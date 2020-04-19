from cthulhu_src.services.exchanges import BaseExchange, get_exchange_by_name
import asyncio
import itertools


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

    async def fetch_prices(self):
        results = await asyncio.gather(*[
            exchanger.fetch_prices()
            for exchanger in self._exchanges
        ])

        prices = list(itertools.chain(*results))
        return prices
