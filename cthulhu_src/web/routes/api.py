"""
API маршруты для получения данных.
"""

import asyncio
import logging
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from cthulhu_src.services.cross_exchange_manager import get_free_transitions
from cthulhu_src.services.forecast import ForecastService
from cthulhu_src.services.historical_data import MultiExchangeHistoricalService
from cthulhu_src.services.progress_exchange_manager import ProgressExchangeManager
from cthulhu_src.web.routes.progress import update_progress

logger = logging.getLogger("excthulhu")

router = APIRouter()


class ForecastArbitrageRequest(BaseModel):
    start_node: str
    amount: float = 1.0
    max_depth: int = 4
    exchanges: List[str] = ["binance", "yobit"]
    auto_fetch_history: bool = True
    history_symbol: Optional[str] = None
    history_hours: int = 24
    forecast_method: str = "mean"
    forecast_horizon: int = 5
    lookback: int = 60


class ForecastRequest(BaseModel):
    prices: List[float]
    methods: List[str] = ["mean"]
    horizons: List[int] = [5]
    lookback: int = 60


class ArbitrageRequest(BaseModel):
    start_node: str
    amount: float = 1.0
    max_depth: int = 4
    exchanges: List[str] = ["binance", "yobit"]
    algorithm: str = "dfs"


@router.get("/exchanges")
async def get_exchanges():
    """Получить список доступных бирж."""
    exchanges = ["binance", "yobit", "hollaex", "oceanex", "poloniex", "upbit", "exmo"]
    return {"exchanges": exchanges}


# Кэш для валют (в реальном приложении лучше использовать Redis)
_currencies_cache = {}


@router.get("/currencies/{exchange}")
async def get_currencies(exchange: str):
    """Получить список доступных валют для биржи."""
    try:
        # Проверяем кэш
        if exchange in _currencies_cache:
            return {
                "exchange": exchange,
                "currencies": _currencies_cache[exchange],
                "cached": True,
            }

        # Создаем временный сервис для получения валют
        historical_service = MultiExchangeHistoricalService([exchange])

        # Получаем реальные валюты с биржи
        currencies = set()

        try:
            # Получаем рынки с биржи
            service = historical_service.services[exchange]

            # Загружаем рынки если нужно
            if hasattr(service.exchange, "load_markets"):
                if hasattr(service.exchange.load_markets, "__call__"):
                    if asyncio.iscoroutinefunction(service.exchange.load_markets):
                        await service.exchange.load_markets()
                    else:
                        service.exchange.load_markets()

            # Извлекаем уникальные базовые валюты из торговых пар
            if hasattr(service.exchange, "markets") and service.exchange.markets:
                for symbol, market in service.exchange.markets.items():
                    if market.get("active", True):  # Только активные рынки
                        base_currency = market.get("base", "")
                        if (
                            base_currency and len(base_currency) <= 10
                        ):  # Фильтруем странные символы
                            currencies.add(base_currency)

            # Если не удалось получить с биржи, используем популярные валюты
            if not currencies:
                currencies = {
                    "BTC",
                    "ETH",
                    "USDT",
                    "BNB",
                    "ADA",
                    "DOT",
                    "LINK",
                    "LTC",
                    "BCH",
                    "XRP",
                }

        except Exception as e:
            logger.warning(f"Не удалось получить валюты с {exchange}: {e}")
            # Fallback на популярные валюты
            currencies = {
                "BTC",
                "ETH",
                "USDT",
                "BNB",
                "ADA",
                "DOT",
                "LINK",
                "LTC",
                "BCH",
                "XRP",
            }

        await historical_service.close()

        # Сортируем валюты для удобства
        sorted_currencies = sorted(list(currencies))

        # Кэшируем результат
        _currencies_cache[exchange] = sorted_currencies

        return {"exchange": exchange, "currencies": sorted_currencies, "cached": False}

    except Exception as e:
        logger.error(f"Ошибка получения валют для {exchange}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/historical-data/{exchange}")
async def get_historical_data(
    exchange: str,
    symbol: str = Query(..., description="Торговая пара (например: BTC/USDT)"),
    hours: int = 24,
    format: str = "prices",
    timeframe: str = "1m"
):
    """Получить исторические данные."""
    try:
        historical_service = MultiExchangeHistoricalService([exchange])

        # Рассчитываем limit по timeframe
        tf_map = {"1m": 1, "5m": 5, "15m": 15, "30m": 30, "1h": 60, "4h": 240, "1d": 1440}
        interval = tf_map.get(timeframe, 1)
        limit = min(1000, max(1, int(hours * 60 / interval))) if "m" in timeframe else min(1000, max(1, int(hours / (interval / 60))))

        if format == "prices":
            try:
                prices = await historical_service.services[exchange].get_price_history(
                    symbol, timeframe=timeframe, hours=hours
                )
                if not prices:
                    raise HTTPException(status_code=404, detail=f"Торговая пара {symbol} не найдена на бирже {exchange}")
                return {
                    "exchange": exchange,
                    "symbol": symbol,
                    "prices": prices,
                    "count": len(prices),
                    "timeframe": timeframe
                }
            except Exception as e:
                if "does not have market symbol" in str(e):
                    raise HTTPException(status_code=404, detail=f"Торговая пара {symbol} не поддерживается на бирже {exchange}")
                else:
                    raise HTTPException(status_code=500, detail=f"Ошибка получения данных: {str(e)}")
        elif format == "ohlcv":
            try:
                ohlcv_data = await historical_service.services[exchange].get_ohlcv(
                    symbol, timeframe=timeframe, limit=limit
                )
                if not ohlcv_data:
                    raise HTTPException(status_code=404, detail=f"Торговая пара {symbol} не найдена на бирже {exchange}")
                return {
                    "exchange": exchange,
                    "symbol": symbol,
                    "ohlcv": ohlcv_data,
                    "count": len(ohlcv_data),
                    "timeframe": timeframe
                }
            except Exception as e:
                if "does not have market symbol" in str(e):
                    raise HTTPException(status_code=404, detail=f"Торговая пара {symbol} не поддерживается на бирже {exchange}")
                else:
                    raise HTTPException(status_code=500, detail=f"Ошибка получения данных: {str(e)}")
        elif format == "info":
            try:
                market_info = await historical_service.services[exchange].get_market_info(
                    symbol
                )
                if not market_info:
                    raise HTTPException(status_code=404, detail=f"Торговая пара {symbol} не найдена на бирже {exchange}")
                return market_info
            except Exception as e:
                if "does not have market symbol" in str(e):
                    raise HTTPException(status_code=404, detail=f"Торговая пара {symbol} не поддерживается на бирже {exchange}")
                else:
                    raise HTTPException(status_code=500, detail=f"Ошибка получения данных: {str(e)}")
        await historical_service.close()
    except Exception as e:
        logger.error(f"Ошибка получения данных: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/forecast")
async def make_forecast(request: ForecastRequest, external_task_id: str = None):
    """Сделать прогноз на основе исторических цен."""
    try:
        if external_task_id:
            update_progress(
                external_task_id, 92, "Выполнение прогнозирования", "forecast"
            )

        forecast_service = ForecastService(lookback=request.lookback)

        forecasts = []
        for method in request.methods:
            method_forecasts = forecast_service.predict(
                request.prices, request.horizons, method
            )
            for horizon, forecast in zip(request.horizons, method_forecasts):
                # Генерируем прогнозируемые цены на основе статистик
                last_price = request.prices[-1]
                forecast_prices = []
                
                for i in range(horizon):
                    # Используем нормальное распределение для генерации прогноза
                    import numpy as np
                    forecast_price = last_price * np.exp(forecast.mu + np.random.normal(0, forecast.sigma))
                    forecast_prices.append(forecast_price)
                    last_price = forecast_price
                
                forecasts.append({
                    "method": method,
                    "horizon": horizon,
                    "mu": forecast.mu,
                    "sigma": forecast.sigma,
                    "confidence": (
                        max(0.0, 1.0 - (forecast.sigma / abs(forecast.mu)))
                        if forecast.sigma > 0
                        else 1.0
                    ),
                    "forecast_prices": forecast_prices
                })

        if external_task_id:
            update_progress(
                external_task_id, 95, "Прогнозирование завершено", "forecast"
            )

        return {
            "prices": request.prices,
            "forecasts": forecasts,
            "lookback": request.lookback,
        }

    except Exception as e:
        logger.error(f"Ошибка прогнозирования: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/arbitrage")
async def find_arbitrage(request: ArbitrageRequest, external_task_id: str = None):
    """Найти арбитражные возможности."""
    import uuid

    task_id = external_task_id if external_task_id else str(uuid.uuid4())

    # Всегда запускаем в фоне и возвращаем task_id
    update_progress(task_id, 0, "Подготовка к поиску арбитража", "init")

    # Запускаем анализ в фоне
    asyncio.create_task(run_arbitrage_analysis(task_id, request))

    return {"task_id": task_id}


async def run_arbitrage_analysis(task_id: str, request: ArbitrageRequest):
    """Выполнить анализ арбитража."""
    logger.info(f"Начинаем анализ арбитража для task_id: {task_id}")
    logger.info(f"Параметры запроса: {request}")
    try:
        update_progress(task_id, 0, "Подготовка к поиску арбитража", "init")

        # Загружаем данные с бирж с отслеживанием прогресса
        def progress_callback(progress: int, message: str):
            # Обновляем прогресс в диапазоне 40-85% (арбитражная часть)
            # 40-50%: загрузка данных с бирж (10%)
            # 50-85%: загрузка книг ордеров (35%)
            if progress <= 100:
                if "Загрузка книг ордеров" in message:
                    # Детальный прогресс загрузки книг ордеров
                    adjusted_progress = 50 + int((progress / 100) * 35)
                else:
                    # Общий прогресс загрузки данных с бирж
                    adjusted_progress = 40 + int((progress / 100) * 10)
                update_progress(task_id, adjusted_progress, message, "arbitrage")

        exchange_manager = ProgressExchangeManager(
            request.exchanges, progress_callback=progress_callback
        )

        try:
            pairs = await exchange_manager.fetch_prices()
        finally:
            await exchange_manager.close()

        pairs += get_free_transitions(request.exchanges)

        # Создаем граф
        from collections import defaultdict

        adj_dict = defaultdict(list)
        for pair in pairs:
            adj_dict[pair.currency_from].append(pair)

        currency_list = list(adj_dict.keys())
        logger.info(
            f"Список валют: {currency_list[:10]}..."
        )  # Показываем первые 10 валют

        # Извлекаем валюту из start_node (например, binance_BTC -> BTC)
        start_currency = (
            request.start_node.split("_")[-1]
            if "_" in request.start_node
            else request.start_node
        )

        if start_currency not in currency_list:
            logger.warning(
                f"Стартовая валюта {start_currency} не найдена в списке: {currency_list[:10]}..."
            )
            # Попробуем найти похожую валюту
            for currency in currency_list:
                if (
                    start_currency.lower() in currency.lower()
                    or currency.lower() in start_currency.lower()
                ):
                    start_currency = currency
                    logger.info(f"Найдена похожая валюта: {start_currency}")
                    break
            else:
                raise HTTPException(
                    status_code=404,
                    detail=f"Стартовая валюта {start_currency} не найдена",
                )

        adj_list = [
            {
                currency_list.index(pair.currency_to): pair.trade_book
                for pair in adj_dict[currency_from]
            }
            for currency_from in currency_list
        ]

        start_node_id = currency_list.index(start_currency)

        # Ищем пути
        from cthulhu_src.services.processor import find_paths

        paths = find_paths(
            adj_list, start_node_id, request.amount, max_depth=request.max_depth
        )

        # Форматируем результаты
        opportunities = []
        for path in paths:
            if len(path) > 1:
                final_amount = path[-1][1]
                profit_percent = (
                    (final_amount - request.amount) / request.amount
                ) * 100

                # Преобразуем индексы в названия валют с биржами
                path_names = []
                for i, node in enumerate(path):
                    node_id = node[0]
                    if 0 <= node_id < len(currency_list):
                        currency_name = currency_list[node_id]
                        # Добавляем информацию о бирже для лучшей читаемости
                        if i == 0:
                            # Первый узел - стартовая валюта
                            path_names.append(f"{currency_name}")
                        else:
                            # Остальные узлы - промежуточные валюты
                            path_names.append(f"{currency_name}")
                        logger.info(f"Путь: {node_id} -> {currency_name}")
                    else:
                        path_names.append(f"Unknown_{node_id}")
                        logger.warning(f"Неизвестный ID узла: {node_id}")

                opportunities.append(
                    {
                        "path": path_names,
                        "profit_percent": profit_percent,
                        "start_amount": request.amount,
                        "final_amount": final_amount,
                    }
                )

        result = {"opportunities": opportunities, "total_found": len(opportunities)}
        logger.info(f"Найдено {len(opportunities)} арбитражных возможностей")
        logger.info(f"Результат: {result}")

        # Сохраняем результаты в глобальном хранилище
        from cthulhu_src.web.routes.progress import _progress_store

        if task_id in _progress_store:
            _progress_store[task_id]["results"] = result
            logger.info(f"Результаты сохранены для task_id: {task_id}")
        else:
            logger.warning(f"Task_id {task_id} не найден в _progress_store")

        update_progress(task_id, 100, "Поиск арбитража завершен", "complete")
        logger.info(f"Анализ арбитража завершен для task_id: {task_id}")

        return result

    except Exception as e:
        update_progress(task_id, 0, f"Ошибка: {str(e)}", "error")
        logger.error(f"Ошибка поиска арбитража: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/forecast-arbitrage")
async def forecast_arbitrage_integrated(request: ForecastArbitrageRequest):
    """Интегрированный поиск арбитража с прогнозированием."""
    import uuid

    task_id = str(uuid.uuid4())

    # Сразу возвращаем task_id и запускаем анализ в фоне
    update_progress(task_id, 0, "Подготовка к анализу", "init")

    # Запускаем анализ в фоне
    asyncio.create_task(run_forecast_arbitrage_analysis(task_id, request))

    return {"task_id": task_id}


async def run_forecast_arbitrage_analysis(
    task_id: str, request: ForecastArbitrageRequest
):
    """Выполнить анализ в фоне."""
    try:
        update_progress(task_id, 0, "Подготовка к анализу", "init")

        # Получаем исторические данные если нужно
        historical_prices = None
        if request.auto_fetch_history:
            update_progress(task_id, 10, "Загрузка исторических данных", "historical")

            if not request.history_symbol:
                currency = (
                    request.start_node.split("_")[-1]
                    if "_" in request.start_node
                    else "BTC"
                )
                history_symbol = f"{currency}/USDT"
            else:
                history_symbol = request.history_symbol

            historical_service = MultiExchangeHistoricalService([request.exchanges[0]])
            historical_prices = await historical_service.services[
                request.exchanges[0]
            ].get_price_history(history_symbol, hours=request.history_hours)
            await historical_service.close()

            update_progress(task_id, 30, "Исторические данные загружены", "historical")

        # Ищем арбитраж
        update_progress(task_id, 40, "Поиск арбитражных возможностей", "arbitrage")

        arbitrage_request = ArbitrageRequest(
            start_node=request.start_node,
            amount=request.amount,
            max_depth=request.max_depth,
            exchanges=request.exchanges,
            algorithm="dfs",
        )
        # Вызываем run_arbitrage_analysis напрямую для получения результата
        arbitrage_result = await run_arbitrage_analysis(task_id, arbitrage_request)

        update_progress(task_id, 85, "Арбитражный анализ завершен", "arbitrage")

        # Делаем прогноз если есть данные
        forecast_result = None
        if historical_prices:
            update_progress(task_id, 90, "Создание прогнозов", "forecast")

            forecast_request = ForecastRequest(
                prices=historical_prices,
                methods=[request.forecast_method],
                horizons=[request.forecast_horizon],
                lookback=request.lookback,
            )
            forecast_result = await make_forecast(forecast_request, task_id)

            update_progress(task_id, 95, "Прогнозы созданы", "forecast")

        update_progress(task_id, 100, "Анализ завершен", "complete")

        # Сохраняем результаты в глобальном хранилище
        from cthulhu_src.web.routes.progress import _progress_store

        if task_id in _progress_store:
            _progress_store[task_id]["results"] = {
                "arbitrage": arbitrage_result,
                "forecast": forecast_result,
                "historical_prices": historical_prices,
                "history_symbol": history_symbol,
            }

    except Exception as e:
        update_progress(task_id, 0, f"Ошибка: {str(e)}", "error")
        logger.error(f"Ошибка интегрированного поиска: {e}")


@router.get("/forecast-arbitrage-results/{task_id}")
async def get_forecast_arbitrage_results(task_id: str):
    """Получить результаты анализа."""
    from cthulhu_src.web.routes.progress import _progress_store

    if task_id not in _progress_store:
        raise HTTPException(status_code=404, detail="Задача не найдена")

    progress_data = _progress_store[task_id]
    results = progress_data.get("results")

    if not results:
        raise HTTPException(status_code=202, detail="Анализ еще выполняется")

    return {
        "task_id": task_id,
        "progress": progress_data.get("progress", 0),
        "message": progress_data.get("message", ""),
        **results,
    }


@router.get("/arbitrage-results/{task_id}")
async def get_arbitrage_results(task_id: str):
    """Получить результаты арбитража."""
    from cthulhu_src.web.routes.progress import _progress_store

    logger.info(f"Запрос результатов для task_id: {task_id}")

    if task_id not in _progress_store:
        logger.warning(f"Task_id {task_id} не найден в _progress_store")
        raise HTTPException(status_code=404, detail="Задача не найдена")

    progress_data = _progress_store[task_id]
    results = progress_data.get("results")

    logger.info(f"Прогресс для task_id {task_id}: {progress_data.get('progress', 0)}%")
    logger.info(f"Результаты для task_id {task_id}: {results is not None}")

    if not results:
        logger.info(f"Результаты еще не готовы для task_id {task_id}")
        raise HTTPException(status_code=202, detail="Анализ еще выполняется")

    logger.info(f"Возвращаем результаты для task_id {task_id}: {len(results.get('opportunities', []))} возможностей")
    return {
        "task_id": task_id,
        "progress": progress_data.get("progress", 0),
        "message": progress_data.get("message", ""),
        **results,
    }
