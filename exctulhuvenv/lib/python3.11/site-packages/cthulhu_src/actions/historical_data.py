"""
Действие для получения исторических данных с бирж.
"""

import asyncio
import logging
from typing import Optional, List

from cthulhu_src.services.historical_data import MultiExchangeHistoricalService


async def run(
    ctx,
    exchange: str,
    symbol: str,
    hours: int = 24,
    count: int = 100,
    output_format: str = "prices",
) -> None:
    """
    Получить исторические данные с биржи.
    
    Args:
        ctx: Контекст CLI
        exchange: Название биржи
        symbol: Торговая пара (например, BTC/USDT)
        hours: Количество часов истории
        count: Количество последних записей
        output_format: Формат вывода (prices, ohlcv, info)
    """
    log = logging.getLogger("excthulhu")
    log.info(f"📊 Получаем исторические данные с {exchange} для {symbol}")
    
    try:
        # Инициализация сервиса
        historical_service = MultiExchangeHistoricalService([exchange])
        
        if output_format == "prices":
            # Получаем только цены
            prices = await historical_service.services[exchange].get_price_history(
                symbol, hours=hours
            )
            
            if prices:
                log.info(f"✅ Получено {len(prices)} цен")
                print(f"Цены: {','.join([str(p) for p in prices])}")
            else:
                log.error("❌ Не удалось получить цены")
                
        elif output_format == "ohlcv":
            # Получаем полные OHLCV данные
            ohlcv_data = await historical_service.services[exchange].get_ohlcv(
                symbol, limit=count
            )
            
            if ohlcv_data:
                log.info(f"✅ Получено {len(ohlcv_data)} OHLCV записей")
                for i, candle in enumerate(ohlcv_data[:5]):  # Показываем первые 5
                    print(f"Запись {i+1}: {candle}")
            else:
                log.error("❌ Не удалось получить OHLCV данные")
                
        elif output_format == "info":
            # Получаем информацию о рынке
            market_info = await historical_service.services[exchange].get_market_info(symbol)
            
            if market_info:
                log.info("✅ Получена информация о рынке")
                for key, value in market_info.items():
                    print(f"{key}: {value}")
            else:
                log.error("❌ Не удалось получить информацию о рынке")
        
        await historical_service.close()
        
    except Exception as e:
        log.error(f"❌ Ошибка получения данных: {e}")
        return 