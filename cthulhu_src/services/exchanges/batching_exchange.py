import asyncio

from cthulhu_src.services.exchanges.base_exchange import BaseExchange


class BatchingExchange(BaseExchange):
    max_batch_size = 20

    async def state_preparation(self, symbols: [str]):
        markets = await self._instance.fetch_order_books(symbols, limit='1')

        results = []
        for symbol, info in markets.items():
            try:
                price = info['bids'][0][0]
            except IndexError:
                continue

            pair = symbol.split('/')
            self.log.debug(f'{self.name}_{pair[0]} - {self.name}_{pair[1]} - {price}')
            results.append((f'{self.name}_{pair[0]}', f'{self.name}_{pair[1]}', price))

        return results

    async def fetch_prices(self):
        markets = await self._instance.fetch_markets()
        symbols = [
            market['symbol']
            for market in markets
        ]

        batches = [
            symbols[i:i + self.max_batch_size]
            for i in range(0, len(symbols), self.max_batch_size)
        ]

        promises = [
            self.state_preparation(batch_symbols)
            for batch_symbols in batches
        ]

        results = [
            result
            for results in await asyncio.gather(*promises)
            for result in results
            if result is not None
        ]

        return results
