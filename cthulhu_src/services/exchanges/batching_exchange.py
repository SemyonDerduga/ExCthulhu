"""Exchange adapter using batch requests for order books."""

from typing import Tuple, Dict, List

from tqdm import tqdm

from cthulhu_src.services.exchanges.base_exchange import BaseExchange
from cthulhu_src.services.pair import Pair, Order


class BatchingExchange(BaseExchange):
    """Exchange that fetches order books in batches."""

    max_batch_size = 20

    async def state_preparation(self, symbols: List[str]) -> List[Pair]:
        """Fetch order books for ``symbols`` and build pair objects."""

        markets: Dict[
            str,
            Dict[
                str,
                List[Tuple[float, float]],
            ],
        ] = await self._with_proxy().fetch_order_books(symbols, limit=self.limit)

        results = []
        for symbol, info in markets.items():
            prices_bid = [
                Order(price=bid_price, amount=bid_amount)
                for bid_price, bid_amount in info["bids"]
            ]
            prices_ask = [
                Order(price=1.0 / ask_price, amount=ask_amount * ask_price)
                for ask_price, ask_amount in info["asks"]
            ]
            if len(prices_bid) == 0 or len(prices_ask) == 0:
                continue

            currency_pair = symbol.split("/")
            self.log.debug(
                f"🔗 {self.name}_{currency_pair[0]} - {self.name}_{currency_pair[1]}"
            )
            results.append(
                Pair(
                    currency_from=f"{self.name}_{currency_pair[0]}",
                    currency_to=f"{self.name}_{currency_pair[1]}",
                    trade_book=prices_bid,
                )
            )
            results.append(
                Pair(
                    currency_from=f"{self.name}_{currency_pair[1]}",
                    currency_to=f"{self.name}_{currency_pair[0]}",
                    trade_book=prices_ask,
                )
            )

        return results

    async def fetch_prices(self) -> List[Pair]:
        """Collect prices for all markets using batch requests."""

        try:
            markets = await self._with_proxy().fetch_markets()
        except Exception as exc:
            self.log.warning(f"⚠️ Failed to fetch markets: {exc}")
            return []
        symbols: [str] = [market["symbol"] for market in markets]

        currency = set([cur for cur_pair in symbols for cur in cur_pair.split("/")])

        self.log.info(f"💱 Received {len(currency)} currency types.")

        batches: List[List[str]] = [
            symbols[i : i + self.max_batch_size]
            for i in range(0, len(symbols), self.max_batch_size)
        ]

        pairs: List[Pair] = []
        for batch_symbols in tqdm(
            batches,
            desc="📈 Fetching books",
            unit="batch",
            dynamic_ncols=True,
        ):
            for pair in await self.state_preparation(batch_symbols):
                if len(pair.trade_book) > 0:
                    pairs.append(pair)

        self.log.info(f"📊 Received {len(pairs)} currency pairs exchange prices.")
        return pairs
