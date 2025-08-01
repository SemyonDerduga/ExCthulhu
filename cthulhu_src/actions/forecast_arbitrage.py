"""
Интегрированное действие для поиска арбитража с прогнозированием.
"""

import logging
import asyncio
from collections import defaultdict
from typing import Optional, List

from cthulhu_src.services.exchange_manager import ExchangeManager
from cthulhu_src.services.forecast_arbitrage import ForecastArbitrageService, ArbitrageOpportunity
from cthulhu_src.services.historical_data import MultiExchangeHistoricalService
from cthulhu_src.services.exchanges.batching_exchange import BatchingExchange
from cthulhu_src.services.cross_exchange_manager import get_free_transitions


async def run(
    ctx,
    max_depth: int,
    exchange_list: list,
    start_node: str,
    start_amount: float,
    cache_dir: str,
    historical_prices: Optional[List[float]] = None,
    forecast_method: str = "mean",
    forecast_horizon: int = 5,
    lookback: int = 60,
    auto_fetch_history: bool = False,
    history_hours: int = 24,
    history_symbol: Optional[str] = None,
    cached: bool = False,
    algorithm: str = "dfs",
    processes: Optional[int] = None,
    prune_ratio: float = 0.0,
    batch_size: int = 20,
    proxy: tuple = (),
) -> None:
    """
    Запустить интегрированный поиск арбитража с прогнозированием.
    
    Эта команда:
    1. Находит арбитражные возможности
    2. Анализирует исторические данные
    3. Делает прогнозы движения цен
    4. Рекомендует действия на основе прогнозов
    """
    log = logging.getLogger("excthulhu")
    log.info(
        f'🔍 Начинаем интегрированный поиск арбитража с прогнозированием (глубина: {max_depth}, биржи: {", ".join(exchange_list)})'
    )

    # Инициализация сервиса прогнозирования
    forecast_service = ForecastArbitrageService(
        lookback=lookback, 
        forecast_method=forecast_method
    )

    # Автоматическое получение исторических данных
    if auto_fetch_history and not historical_prices:
        log.info("📊 Автоматически получаем исторические данные...")
        
        # Определяем символ для исторических данных
        if not history_symbol:
            # Извлекаем валюту из start_node (например, binance_BTC -> BTC/USDT)
            currency = start_node.split('_')[-1] if '_' in start_node else 'BTC'
            history_symbol = f"{currency}/USDT"
        
        try:
            # Получаем исторические данные с первой биржи
            historical_service = MultiExchangeHistoricalService([exchange_list[0]], list(proxy))
            
            historical_prices = await historical_service.services[exchange_list[0]].get_price_history(
                history_symbol, 
                hours=history_hours
            )
            
            await historical_service.close()
            
            if historical_prices:
                log.info(f"✅ Получено {len(historical_prices)} исторических цен для {history_symbol}")
            else:
                log.warning(f"⚠️ Не удалось получить исторические данные для {history_symbol}")
                
        except Exception as e:
            log.error(f"❌ Ошибка получения исторических данных: {e}")

    log.info("⬇️ Загружаем данные с бирж...")

    BatchingExchange.max_batch_size = batch_size
    exchange_manager = ExchangeManager(
        exchange_list, proxy, cached=cached, cache_dir=cache_dir
    )
    
    try:
        pairs = await exchange_manager.fetch_prices()
    finally:
        await exchange_manager.close()

    pairs += get_free_transitions(exchange_list)

    log.info("✅ Загрузка завершена")

    log.info("⚙️ Подготавливаем данные...")

    # Создаем граф обменных курсов
    adj_dict = defaultdict(list)
    for pair in pairs:
        adj_dict[pair.currency_from].append(pair)

    currency_list = list(adj_dict.keys())

    adj_list = [
        {
            currency_list.index(pair.currency_to): pair.trade_book
            for pair in adj_dict[currency_from]
        }
        for currency_from in currency_list
    ]

    log.info("✅ Подготовка данных завершена")

    if start_node not in currency_list:
        log.error(f"❌ Стартовая валюта {start_node} недоступна в загруженных данных.")
        return

    start_node_id = currency_list.index(start_node)

    log.info("🔄 Обрабатываем данные с прогнозированием...")

    # Поиск возможностей с прогнозированием
    opportunities = forecast_service.find_opportunities_with_forecast(
        adj_list=adj_list,
        start_node=start_node_id,
        start_amount=start_amount,
        max_depth=max_depth,
        prune_ratio=prune_ratio,
        num_workers=processes,
        historical_prices=historical_prices,
        forecast_horizon=forecast_horizon,
    )

    # Выводим результаты
    log.info(f"📊 Найдено {len(opportunities)} арбитражных возможностей")

    if not opportunities:
        log.info("❌ Прибыльные возможности не найдены")
        return

    # Анализ рыночных трендов если есть исторические данные
    if historical_prices:
        log.info("📈 Анализируем рыночные тренды...")
        trend_analysis = forecast_service.analyze_market_trends(historical_prices)
        
        if "error" not in trend_analysis:
            trend = trend_analysis.get("overall_trend", "neutral")
            log.info(f"📊 Общий тренд рынка: {trend}")
        else:
            log.warning(f"⚠️ Ошибка анализа трендов: {trend_analysis['error']}")

    # Выводим топ-5 возможностей
    log.info("🏆 Топ-5 арбитражных возможностей:")
    
    for i, opportunity in enumerate(opportunities[:5], 1):
        log.info(f"\n{i}. Путь: {' -> '.join([f'{node[0]}' for node in opportunity.path])}")
        log.info(f"   💰 Прибыль: {opportunity.profit_percent:.2f}%")
        
        if opportunity.forecast:
            log.info(f"   📈 Прогноз: {opportunity.forecast.mu:.4f} (уверенность: {opportunity.forecast_confidence:.2f})")
            log.info(f"   🎯 Рекомендация: {opportunity.recommended_action}")
        else:
            log.info(f"   📈 Прогноз: недоступен (нет исторических данных)")

    log.info(f"\n✅ Интегрированный поиск завершен. Найдено {len(opportunities)} возможностей.") 