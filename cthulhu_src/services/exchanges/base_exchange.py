import asyncio
import logging

import ccxt.async_support as ccxt

class BaseExchange:
    currency_blacklist = []
    opts = {
        'enableRateLimit': True,
    }
    name = ''
    log = logging.getLogger('excthulhu')

    def __init__(self):
        self._instance = getattr(ccxt, self.name)(self.opts)

    async def close(self):
        await self._instance.close()

    async def state_preparation(self, symbol):
        result = await self._instance.fetch_order_book(symbol, limit=5)
        pair = symbol.split('/')

        try:
            price = result['bids'][0][0]
            self.log.debug(f'{self.name}_{pair[0]} - {self.name}_{pair[1]} - {price}')
            return f'{self.name}_{pair[0]}', f'{self.name}_{pair[1]}', price
        except IndexError:
            return None

    async def fetch_prices(self):
        markets = await self._instance.fetch_markets()

        symbols = [
            market['symbol']
            for market in markets
        ]
        self.log.info(f'Received {len(markets)} сurrency pairs.')

        promises = [
            self.state_preparation(symbol)
            for symbol in symbols
        ]

        results = [
            result
            for result in await asyncio.gather(*promises)
            if result is not None
        ]
        self.log.info(f'Received {len(results)} сurrency pairs exchange prices.')

        return results
