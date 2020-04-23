import asyncio
from typing import Tuple, Dict, List

from cthulhu_src.services.exchanges.base_exchange import BaseExchange
from cthulhu_src.services.pair import Pair, Trade


class BatchingExchange(BaseExchange):
    max_batch_size = 20

    async def state_preparation(self, symbols: List[str], limit: int = 20) -> List[Pair]:
        markets: Dict[
            str,
            Dict[
                str,
                List[Tuple[float, float]],
            ],
        ] = await self._instance.fetch_order_books(symbols, limit=str(limit))

        results = []
        for symbol, info in markets.items():
            prices_bid = [
                Trade(price=bid_price, amount=bid_amount)
                for bid_price, bid_amount in info['bids']
            ]
            prices_ask = [
                Trade(price=1.0 / ask_price, amount=ask_amount)
                for ask_price, ask_amount in info['asks']
            ]

            currency_pair = symbol.split('/')
            self.log.debug(f'{self.name}_{currency_pair[0]} - {self.name}_{currency_pair[1]}')
            results.append(Pair(currency_from=currency_pair[0],
                                currency_to=currency_pair[1],
                                trade_book=prices_bid))
            results.append(Pair(currency_from=currency_pair[1],
                                currency_to=currency_pair[0],
                                trade_book=prices_ask))

        return results

    async def fetch_prices(self) -> List[Pair]:
        markets = await self._instance.fetch_markets()
        symbols: [str] = [
            market['symbol']
            for market in markets
        ]

        batches: List[List[str]] = [
            symbols[i:i + self.max_batch_size]
            for i in range(0, len(symbols), self.max_batch_size)
        ]

        promises = [
            self.state_preparation(batch_symbols)
            for batch_symbols in batches
        ]

        pairs: List[Pair] = [
            pair
            for pairs in await asyncio.gather(*promises)
            for pair in pairs
            if len(pair.trade_book) > 0
        ]

        self.log.info(f'Received {len(pairs)} сurrency pairs exchange prices.')
        return pairs
