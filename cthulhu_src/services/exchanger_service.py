from cthulhu_src.services.exchangers import yobit, binance, base_exchanger
import asyncio
import itertools


class ExchangerManager:
    exchanger_classes = (
        # yobit.Yobit,
        binance.Binance,
    )

    def __init__(self):
        self._exchangers: [base_exchanger.BaseExchanger] = [
            Exchanger()
            for Exchanger in self.exchanger_classes
        ]

    async def close(self):
        await asyncio.gather(*[
            exchanger.close()
            for exchanger in self._exchangers
        ])

    async def fetch_prices(self):
        results = await asyncio.gather(*[
            exchanger.fetch_prices()
            for exchanger in self._exchangers
        ])

        prices = list(itertools.chain(*results))
        return prices
