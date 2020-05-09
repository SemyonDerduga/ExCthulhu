import asyncio
import logging
import traceback
from contextlib import contextmanager, asynccontextmanager
from typing import Tuple, Dict, List, Optional
from aiohttp import ClientSession
import ccxt.async_support as ccxt
from aiohttp_proxy import ProxyConnector

from cthulhu_src.services.pair import Pair, Order
from cthulhu_src.services.proxy_manager import ProxyManager


class BaseExchange:
    currency_blacklist = []
    opts = {
        'enableRateLimit': True,
    }
    name = ''
    limit = 2000
    fee = 0
    log = logging.getLogger('excthulhu')

    def __init__(self, proxy_manager: Optional[ProxyManager] = None):
        exchange_class = getattr(ccxt, self.name)
        self._proxy_manager = proxy_manager
        self._session_lock = asyncio.Lock()

        self._sessions = []
        if proxy_manager is not None:
            for proxy in proxy_manager.get_active_proxies():
                connector = ProxyConnector.from_url(proxy)
                proxy_url = connector.proxy_url
                self._sessions.append((proxy_url, ClientSession(connector=connector), asyncio.Lock()))

            if 'rateLimit' in self.opts:
                self.opts['rateLimit'] = int(self.opts['rateLimit'] / len(self._sessions))
            else:
                self.opts['rateLimit'] = int(exchange_class().describe()['rateLimit'] / len(self._sessions))

        self._session_index = -1

        self._instance = exchange_class(self.opts)

    async def close(self):
        for session in self._sessions:
            await session[1].close()
        await self._instance.close()

    @asynccontextmanager
    async def get_api(self):
        api = self._instance

        if self._proxy_manager is not None:
            session_index = self._session_index
            proxy_url, session, lock = self._sessions[session_index]

            await lock.acquire()
            api.session = session
            self._session_index = (self._session_index + 1) % len(self._sessions)

            self.log.debug(f'use {proxy_url}')

            try:
                yield api
            except (ccxt.DDoSProtection, ccxt.RequestTimeout, ccxt.AuthenticationError,
                    ccxt.ExchangeNotAvailable, ccxt.ExchangeError, ccxt.NetworkError) as e:
                self.log.exception(e)

                await session.close()
                new_proxy_url = await self._proxy_manager.change_proxy(str(proxy_url))
                api.session = ClientSession(connector=ProxyConnector.from_url(new_proxy_url))
            finally:
                lock.release()
                return

        yield api

    async def state_preparation(self, symbol: str) -> List[Pair]:
        while True:
            async with self.get_api() as api:
                result: Dict[
                    str,
                    Tuple[float, float],
                ] = await api.fetch_order_book(symbol, limit=str(self.limit))
                break

        prices_bid = [
            Order(price=bid_price, amount=bid_amount)
            for bid_price, bid_amount in result['bids']
        ]
        prices_ask = [
            Order(price=1.0 / ask_price, amount=ask_amount * ask_price)
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
        while True:
            async with self.get_api() as api:
                markets = await api.fetch_markets()
                break

        symbols = [
            market['symbol']
            for market in markets
        ]

        currency = set([
            cur
            for cur_pair in symbols
            for cur in cur_pair.split('/')
        ])

        self.log.info(f'Received {len(currency)} сurrency.')

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

    @classmethod
    def calc_fee(cls, amount: float) -> float:
        return amount * (1.0 + cls.fee)
