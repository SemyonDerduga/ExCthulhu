import asyncio
import logging
from typing import Tuple, Dict, List
import ccxt.async_support as ccxt

from cthulhu_src.services.pair import Pair, Order


class BaseExchange:
    currency_blacklist = []
    opts = {
        'enableRateLimit': True,
    }
    name = ''
    log = logging.getLogger('excthulhu')

    def __init__(self, proxies=()):
        self._instance = getattr(ccxt, self.name)(self.opts)
        self._proxies = proxies
        self._proxy_index = 0

    async def close(self):
        await self._instance.close()

    def _with_proxy(self):
        api = self._instance
        if len(self._proxies) > 0:
            api.proxy = self._proxies[self._proxy_index]
            self._proxy_index = (self._proxy_index + 1) % len(self._proxies)

        return api

    async def state_preparation(self, symbol: str, limit: int = 20) -> List[Pair]:
        result: Dict[
            str,
            Tuple[float, float],
        ] = await self._with_proxy().fetch_order_book(symbol, limit=str(limit))

        prices_bid = [
            Order(price=bid_price, amount=bid_amount)
            for bid_price, bid_amount in result['bids']
        ]
        prices_ask = [
            Order(price=1.0 / ask_price, amount=ask_amount)
            for ask_price, ask_amount in result['asks']
        ]

        if len(prices_bid) == 0 or len(prices_ask) == 0:
            return []

        pair = symbol.split('/')
        self.log.debug(f'{self.name}_{pair[0]} - {self.name}_{pair[1]}')
        return [Pair(currency_from=f'{self.name}_{pair[0]}',
                     currency_to=f'{self.name}_{pair[1]}',
                     trade_book=prices_bid),
                Pair(currency_from=f'{self.name}_{pair[1]}',
                     currency_to=f'{self.name}_{pair[0]}',
                     trade_book=prices_ask)]

    async def fetch_prices(self) -> List[Pair]:
        markets = await self._with_proxy().fetch_markets()

        symbols = [
            market['symbol']
            for market in markets
        ]
        self.log.info(f'Received {len(markets)} сurrency pairs.')

        promises = [
            self.state_preparation(symbol)
            for symbol in symbols
        ]

        pairs: List[Pair] = [
            pair
            for pairs in await asyncio.gather(*promises)
            for pair in pairs
            if len(pair.trade_book) > 0
        ]

        self.log.info(f'Received {len(pairs)} сurrency pairs exchange prices.')
        return pairs
