import asyncio

import ccxt.async_support as ccxt


class BaseExchange:
    currency_blacklist = []
    opts = {
        'enableRateLimit': True,
    }
    name = ''

    def __init__(self):
        self._instance = getattr(ccxt, self.name)(self.opts)

    async def close(self):
        await self._instance.close()

    async def fetch_prices(self):
        markets = await self._instance.fetch_markets()
        symbols = [
            market['symbol']
            for market in markets
        ]

        promises = [
            self._instance.fetch_order_book(symbol, limit=5)
            for symbol in symbols
        ]

        results = await asyncio.gather(*promises, return_exceptions=True)
        prices = []
        for i, result in enumerate(results):
            if len(result['bids']) == 0 or len(result['bids'][0]) == 0:
                continue

            pair = symbols[i].split('/')
            price = result['bids'][0][0]
            prices.append((f'{self.name}_{pair[0]}', f'{self.name}_{pair[1]}', price))

        return prices
