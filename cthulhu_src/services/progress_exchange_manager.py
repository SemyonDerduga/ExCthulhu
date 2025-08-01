"""
ExchangeManager с поддержкой отслеживания прогресса.
"""

import asyncio
import logging
from typing import List, Optional, Callable
from cthulhu_src.services.exchange_manager import ExchangeManager
from cthulhu_src.services.pair import Pair

logger = logging.getLogger("excthulhu")


class ProgressBaseExchange:
    """Обертка для BaseExchange с поддержкой прогресса."""
    
    def __init__(self, exchange, progress_callback: Optional[Callable] = None):
        self.exchange = exchange
        self.progress_callback = progress_callback
    
    async def fetch_prices(self) -> List[Pair]:
        """Загрузить цены с отслеживанием прогресса."""
        try:
            markets = await self.exchange._with_proxy().fetch_markets()
        except Exception as exc:
            self.exchange.log.warning(f"⚠️ Failed to fetch markets: {exc}")
            return []

        symbols = [market["symbol"] for market in markets]
        currency = set([cur for cur_pair in symbols for cur in cur_pair.split("/")])
        
        self.exchange.log.info(f"💱 Received {len(currency)} currency types.")

        pairs: List[Pair] = []
        
        async def fetch(symbol: str) -> List[Pair]:
            try:
                return await self.exchange.state_preparation(symbol)
            except Exception as exc:
                self.exchange.log.warning(f"⚠️ Failed to fetch {symbol}: {exc}")
                return []

        batch_size = self.exchange.max_concurrent_requests
        total_batches = (len(symbols) + batch_size - 1) // batch_size
        
        for i in range(0, len(symbols), batch_size):
            batch = symbols[i : i + batch_size]
            current_batch = i // batch_size + 1
            
            if self.progress_callback:
                progress_percent = int((current_batch / total_batches) * 100)
                self.progress_callback(progress_percent, f"Загрузка книг ордеров: {current_batch}/{total_batches}")
            
            self.exchange.log.debug(
                f"🔄 Processing symbols {i+1}-{min(i+batch_size, len(symbols))} of {len(symbols)}"
            )
            results = await asyncio.gather(*[fetch(symbol) for symbol in batch])
            for pairs_batch in results:
                pairs.extend([p for p in pairs_batch if len(p.trade_book) > 0])

        self.exchange.log.info(f"📊 Received {len(pairs)} currency pairs exchange prices.")
        return pairs


class ProgressExchangeManager(ExchangeManager):
    """
    ExchangeManager с поддержкой отслеживания прогресса загрузки данных.
    """
    
    def __init__(self, exchanges: List[str], proxies: tuple = (), cached: bool = False, 
                 cache_dir: str = "~/.cache/cthulhu", progress_callback: Optional[Callable] = None):
        """
        Инициализация менеджера с поддержкой прогресса.
        
        Args:
            exchanges: Список бирж
            proxies: Прокси
            cached: Использовать кэш
            cache_dir: Директория кэша
            progress_callback: Функция обратного вызова для прогресса
        """
        super().__init__(exchanges, proxies, cached, cache_dir)
        self.progress_callback = progress_callback
        self.total_exchanges = len(exchanges)
        self.current_exchange = 0
    
    async def fetch_prices(self) -> List[Pair]:
        """Загрузить цены с отслеживанием прогресса."""
        if self.progress_callback:
            self.progress_callback(0, "Начало загрузки данных с бирж")
        
        results = []
        for i, exchange_name in enumerate(self._exchange_names):
            try:
                if self.progress_callback:
                    progress = int((i / self.total_exchanges) * 70)  # 70% для загрузки данных
                    self.progress_callback(progress, f"Загрузка данных с {exchange_name}")
                
                if exchange_name not in self._cached_exchanges:
                    # Создаем обертку с прогрессом для загрузки книг ордеров
                    exchange = self._exchanges[exchange_name]
                    progress_exchange = ProgressBaseExchange(exchange, self.progress_callback)
                    exchange_prices = await progress_exchange.fetch_prices()
                else:
                    # Для кэшированных данных используем обычный метод
                    exchange_prices = await self.fetch_exchange_prices(exchange_name)
                
                results.extend(exchange_prices)
                
            except Exception as e:
                logger.error(f"Ошибка загрузки с {exchange_name}: {e}")
                if self.progress_callback:
                    self.progress_callback(progress, f"Ошибка загрузки с {exchange_name}")
        
        if self.progress_callback:
            self.progress_callback(70, "Загрузка данных завершена")
        
        return results 