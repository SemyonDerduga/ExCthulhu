"""
Сервис для получения исторических данных с бирж.
"""

import asyncio
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import ccxt

logger = logging.getLogger("excthulhu")


class HistoricalDataService:
    """
    Сервис для получения исторических данных с бирж.
    
    Поддерживает получение:
    - OHLCV данных (Open, High, Low, Close, Volume)
    - Временных рядов цен
    - Данных о торговых объемах
    """
    
    def __init__(self, exchange_name: str, proxies: List[str] = None):
        """
        Инициализация сервиса.
        
        Args:
            exchange_name: Название биржи (например, 'binance')
            proxies: Список прокси для подключения
        """
        self.exchange_name = exchange_name
        self.proxies = proxies or []
        
        # Инициализация CCXT биржи
        exchange_class = getattr(ccxt, exchange_name)
        self.exchange = exchange_class({
            'proxies': {
                'http': proxies[0] if proxies else None,
                'https': proxies[0] if proxies else None,
            } if proxies else {}
        })
    
    async def get_ohlcv(
        self, 
        symbol: str, 
        timeframe: str = '1m', 
        limit: int = 100,
        since: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Получить OHLCV данные.
        
        Args:
            symbol: Торговая пара (например, 'BTC/USDT')
            timeframe: Временной интервал ('1m', '5m', '1h', '1d')
            limit: Количество свечей
            since: Время начала в миллисекундах
        
        Returns:
            Список словарей с OHLCV данными
        """
        try:
            # Загружаем рынки если нужно
            if hasattr(self.exchange, 'load_markets'):
                if hasattr(self.exchange.load_markets, '__call__'):
                    if asyncio.iscoroutinefunction(self.exchange.load_markets):
                        await self.exchange.load_markets()
                    else:
                        self.exchange.load_markets()
            
            # Получаем OHLCV данные
            if hasattr(self.exchange, 'fetch_ohlcv'):
                if asyncio.iscoroutinefunction(self.exchange.fetch_ohlcv):
                    ohlcv = await self.exchange.fetch_ohlcv(symbol, timeframe, since, limit)
                else:
                    ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, since, limit)
            else:
                logger.error(f"❌ Биржа {self.exchange_name} не поддерживает fetch_ohlcv")
                return []
            
            # Преобразуем в удобный формат
            result = []
            for candle in ohlcv:
                result.append({
                    'timestamp': candle[0],
                    'datetime': datetime.fromtimestamp(candle[0] / 1000),
                    'open': candle[1],
                    'high': candle[2],
                    'low': candle[3],
                    'close': candle[4],
                    'volume': candle[5]
                })
            
            logger.info(f"📊 Получено {len(result)} OHLCV записей для {symbol}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Ошибка получения OHLCV для {symbol}: {e}")
            return []
    
    async def get_price_history(
        self, 
        symbol: str, 
        timeframe: str = '1m', 
        hours: int = 24
    ) -> List[float]:
        """
        Получить историю цен для прогнозирования.
        
        Args:
            symbol: Торговая пара
            timeframe: Временной интервал
            hours: Количество часов истории
        
        Returns:
            Список цен (close prices)
        """
        try:
            # Вычисляем время начала
            since = int((datetime.now() - timedelta(hours=hours)).timestamp() * 1000)
            
            # Получаем OHLCV данные
            ohlcv_data = await self.get_ohlcv(symbol, timeframe, limit=1000, since=since)
            
            # Извлекаем цены закрытия
            prices = [candle['close'] for candle in ohlcv_data]
            
            logger.info(f"📈 Получено {len(prices)} цен для {symbol}")
            return prices
            
        except Exception as e:
            logger.error(f"❌ Ошибка получения истории цен для {symbol}: {e}")
            return []
    
    async def get_recent_prices(
        self, 
        symbol: str, 
        count: int = 100
    ) -> List[float]:
        """
        Получить последние цены для быстрого анализа.
        
        Args:
            symbol: Торговая пара
            count: Количество последних цен
        
        Returns:
            Список последних цен
        """
        try:
            ohlcv_data = await self.get_ohlcv(symbol, '1m', limit=count)
            prices = [candle['close'] for candle in ohlcv_data]
            
            logger.info(f"💰 Получено {len(prices)} последних цен для {symbol}")
            return prices
            
        except Exception as e:
            logger.error(f"❌ Ошибка получения последних цен для {symbol}: {e}")
            return []
    
    async def get_market_info(self, symbol: str) -> Dict[str, Any]:
        """
        Получить информацию о рынке.
        
        Args:
            symbol: Торговая пара
        
        Returns:
            Словарь с информацией о рынке
        """
        try:
            # Загружаем рынки если нужно
            if hasattr(self.exchange, 'load_markets'):
                if hasattr(self.exchange.load_markets, '__call__'):
                    if asyncio.iscoroutinefunction(self.exchange.load_markets):
                        await self.exchange.load_markets()
                    else:
                        self.exchange.load_markets()
            
            if symbol not in self.exchange.markets:
                logger.error(f"❌ Торговая пара {symbol} не найдена на {self.exchange_name}")
                return {}
            
            market = self.exchange.markets[symbol]
            
            # Получаем текущий тикер
            if hasattr(self.exchange, 'fetch_ticker'):
                if asyncio.iscoroutinefunction(self.exchange.fetch_ticker):
                    ticker = await self.exchange.fetch_ticker(symbol)
                else:
                    ticker = self.exchange.fetch_ticker(symbol)
            else:
                logger.error(f"❌ Биржа {self.exchange_name} не поддерживает fetch_ticker")
                return {}
            
            return {
                'symbol': symbol,
                'base': market['base'],
                'quote': market['quote'],
                'active': market['active'],
                'current_price': ticker['last'],
                'bid': ticker['bid'],
                'ask': ticker['ask'],
                'volume_24h': ticker['baseVolume'],
                'change_24h': ticker['percentage'],
                'high_24h': ticker['high'],
                'low_24h': ticker['low']
            }
            
        except Exception as e:
            logger.error(f"❌ Ошибка получения информации о рынке {symbol}: {e}")
            return {}
    
    async def close(self):
        """Закрыть соединение с биржей."""
        if hasattr(self.exchange, 'close'):
            if asyncio.iscoroutinefunction(self.exchange.close):
                await self.exchange.close()
            else:
                self.exchange.close()


class MultiExchangeHistoricalService:
    """
    Сервис для работы с историческими данными нескольких бирж.
    """
    
    def __init__(self, exchange_names: List[str], proxies: List[str] = None):
        """
        Инициализация мультибиржевого сервиса.
        
        Args:
            exchange_names: Список названий бирж
            proxies: Список прокси
        """
        self.services = {
            name: HistoricalDataService(name, proxies)
            for name in exchange_names
        }
    
    async def get_prices_from_all_exchanges(
        self, 
        symbol: str, 
        count: int = 100
    ) -> Dict[str, List[float]]:
        """
        Получить цены с всех бирж.
        
        Args:
            symbol: Торговая пара
            count: Количество цен
        
        Returns:
            Словарь {биржа: [цены]}
        """
        tasks = []
        for exchange_name, service in self.services.items():
            task = service.get_recent_prices(symbol, count)
            tasks.append((exchange_name, task))
        
        results = {}
        for exchange_name, task in tasks:
            try:
                prices = await task
                if prices:
                    results[exchange_name] = prices
            except Exception as e:
                logger.warning(f"⚠️ Ошибка получения данных с {exchange_name}: {e}")
        
        return results
    
    async def close(self):
        """Закрыть все соединения."""
        close_tasks = []
        for service in self.services.values():
            close_tasks.append(service.close())
        
        if close_tasks:
            await asyncio.gather(*close_tasks, return_exceptions=True) 