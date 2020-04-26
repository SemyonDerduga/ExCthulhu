import asyncio
import logging
from typing import Tuple, Dict, List
import ccxt.async_support as ccxt

from cthulhu_src.services.pair import Pair, Trade


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

    async def state_preparation(self, symbol: str, limit: int = 20) -> Tuple[Pair, Pair]:
        result: Dict[
            str,
            Tuple[float, float],
        ] = await self._instance.fetch_order_book(symbol, limit=str(limit))

        prices_bid = [
            Trade(price=bid_price, amount=bid_amount)
            for bid_price, bid_amount in result['bids']
        ]
        prices_ask = [
            Trade(price=1.0 / ask_price, amount=ask_amount)
            for ask_price, ask_amount in result['asks']
        ]
        pair = symbol.split('/')
        self.log.debug(f'{self.name}_{pair[0]} - {self.name}_{pair[1]}')
        return (Pair(currency_from=f'{self.name}_{pair[0]}',
                     currency_to=f'{self.name}_{pair[1]}',
                     trade_book=prices_bid),
                Pair(currency_from=f'{self.name}_{pair[1]}',
                     currency_to=f'{self.name}_{pair[0]}',
                     trade_book=prices_ask))

    async def fetch_prices(self) -> List[Pair]:
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

        pairs: List[Pair] = [
            pair
            for pairs in await asyncio.gather(*promises)
            for pair in pairs
            if len(pair.trade_book) > 0
        ]

        self.log.info(f'Received {len(pairs)} сurrency pairs exchange prices.')
        return pairs
