import asyncio
import itertools
import json
import os
import logging
from pathlib import Path
from typing import List, Dict

from cthulhu_src.services.exchanges import (
    BaseExchange,
    Binance,
    Dsx,
    Exmo,
    Hollaex,
    Oceanex,
    Poloniex,
    Tidex,
    Upbit,
    Yobit,
    GenericExchange,
)
from cthulhu_src.services.pair import Pair, Order

exchanges_instances = {
    "binance": Binance,
    "dsx": Dsx,
    "exmo": Exmo,
    "hollaex": Hollaex,
    "oceanex": Oceanex,
    "poloniex": Poloniex,
    "tidex": Tidex,
    "upbit": Upbit,
    "yobit": Yobit,
}


def get_exchange_by_name(exchange_name, proxies):
    if exchange_name in exchanges_instances:
        return exchanges_instances[exchange_name](proxies)
    else:
        return GenericExchange(exchange_name, proxies)


class ExchangeManager:
    """
    ExchangeManager - asynchronous data collection from exchanges
    """

    def __init__(
        self,
        exchanges: List[str],
        proxies=(),
        cached=False,
        cache_dir="~/.cache/cthulhu",
    ):
        """
        Creates cache directory
        Creates list of cached exchanges
        Inits list of not cached exchange instances.

        :param exchanges: list of exchanges
        :param proxies:
        """
        self._cached = cached
        self._exchange_names = exchanges
        self._cached_exchanges = []

        if self._cached:
            cache_dir_path = Path(os.path.expanduser(cache_dir))
            cache_dir_path.mkdir(parents=True, exist_ok=True)
            self._cache_dir = cache_dir_path.absolute()
            self._cached_exchanges = [
                name[: name.rindex(".json")]
                for name in os.listdir(self._cache_dir)
                if os.path.isfile(f"{self._cache_dir}/{name}")
                and name.endswith(".json")
            ]

        self._exchanges: Dict[str, BaseExchange] = {
            name: get_exchange_by_name(name, proxies)
            for name in exchanges
            if name not in self._cached_exchanges
        }

    async def close(self):
        await asyncio.gather(
            *[exchange.close() for exchange in self._exchanges.values()]
        )

    async def fetch_prices(self) -> List[Pair]:
        results = await asyncio.gather(
            *[
                self.fetch_exchange_prices(exchange_name)
                for exchange_name in self._exchange_names
            ],
            return_exceptions=True,
        )

        prices: List[Pair] = []
        for result in results:
            if isinstance(result, Exception):
                logging.getLogger("excthulhu").warning(
                    f"Failed to fetch exchange prices: {result}"
                )
                continue
            prices.extend(result)

        return prices

    async def fetch_exchange_prices(self, exchange_name: str) -> List[Pair]:
        if exchange_name not in self._cached_exchanges:
            exchange = self._exchanges[exchange_name]
            try:
                prices = await exchange.fetch_prices()
            except Exception as exc:
                logging.getLogger("excthulhu").warning(
                    f"Failed to fetch {exchange_name}: {exc}"
                )
                return []
            if not self._cached:
                return prices

            with open(f"{self._cache_dir}/{exchange_name}.json", "w+") as file:
                json.dump(
                    [
                        {
                            "currency_from": pair.currency_from,
                            "currency_to": pair.currency_to,
                            "trade_book": [
                                (order.price, order.amount) for order in pair.trade_book
                            ],
                        }
                        for pair in prices
                    ],
                    file,
                )
                return prices

        try:
            with open(f"{self._cache_dir}/{exchange_name}.json") as file:
                data = json.load(file)
        except Exception as exc:
            logging.getLogger("excthulhu").warning(
                f"Failed to load cache for {exchange_name}: {exc}"
            )
            return []
        return [
                Pair(
                    currency_from=pair["currency_from"],
                    currency_to=pair["currency_to"],
                    trade_book=[
                        Order(
                            price=order[0],
                            amount=order[1],
                        )
                        for order in pair["trade_book"]
                    ],
                )
                for pair in data
            ]
