import asyncio
from typing import Tuple, Dict, List
import ccxt

from cthulhu_src.services.exchanges.base_exchange import BaseExchange
from cthulhu_src.services.pair import Pair, Order


class BatchingExchange(BaseExchange):
    max_batch_size = 20

    async def state_preparation(self, symbols: List[str]) -> List[Pair]:
        api, session_id = self._get_api()
        while True:
            try:
                markets: Dict[
                    str,
                    Dict[
                        str,
                        List[Tuple[float, float]],
                    ],
                ] = await api.fetch_order_books(symbols, limit=str(self.limit))
                break
            except (ccxt.DDoSProtection, ccxt.RequestTimeout, ccxt.AuthenticationError,
                    ccxt.ExchangeNotAvailable, ccxt.ExchangeError, ccxt.NetworkError):
                if self._proxy_manager is None:
                    raise

                api.session = await self._change_session(session_id)

        results = []
        for symbol, info in markets.items():
            prices_bid = [
                Order(price=bid_price, amount=bid_amount)
                for bid_price, bid_amount in info['bids']
            ]
            prices_ask = [
                Order(price=1.0 / ask_price, amount=ask_amount * ask_price)
                for ask_price, ask_amount in info['asks']
            ]
            if len(prices_bid) == 0 or len(prices_ask) == 0:
                continue

            currency_pair = symbol.split('/')
            self.log.debug(f'{self.name}_{currency_pair[0]} - {self.name}_{currency_pair[1]}')
            results.append(Pair(currency_from=f'{self.name}_{currency_pair[0]}',
                                currency_to=f'{self.name}_{currency_pair[1]}',
                                trade_book=prices_bid))
            results.append(Pair(currency_from=f'{self.name}_{currency_pair[1]}',
                                currency_to=f'{self.name}_{currency_pair[0]}',
                                trade_book=prices_ask))

        return results

    async def fetch_prices(self) -> List[Pair]:
        api, session_id = self._get_api()
        while True:
            try:
                markets = await api.fetch_markets()
                break
            except (ccxt.DDoSProtection, ccxt.RequestTimeout, ccxt.AuthenticationError,
                    ccxt.ExchangeNotAvailable, ccxt.ExchangeError, ccxt.NetworkError):
                if self._proxy_manager is None:
                    raise

                api.session = await self._change_session(session_id)

        symbols: [str] = [
            market['symbol']
            for market in markets
        ]

        currency = set([
            cur
            for cur_pair in symbols
            for cur in cur_pair.split('/')
        ])

        self.log.info(f'Received {len(currency)} сurrency.')

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
