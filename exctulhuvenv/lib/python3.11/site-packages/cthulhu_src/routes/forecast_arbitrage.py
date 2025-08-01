import click
import asyncio
from cthulhu_src.actions.forecast_arbitrage import run as run_cmd

"""
    Команда для интегрированного поиска арбитража с прогнозированием.
"""


@click.command()
@click.pass_context
@click.option("-d", "--max-depth", type=int, default=4, help="Максимальная глубина поиска транзакций")
@click.option("-s", "--start", required=True, help="Точка входа в формате 'биржа_валюта' (например: binance_BTC)")
@click.option("-a", "--amount", type=float, default=1.0, help="Количество исходной валюты")
@click.option("-c", "--cached", type=bool, default=False, help="Использовать кешированные данные бирж", is_flag=True)
@click.option("--cache-dir", default="~/.cache/cthulhu", help="Путь к папке с кешированными данными")
@click.option("-e", "--exchange-list", multiple=True, default=["yobit", "binance"])
@click.option("--algorithm", type=click.Choice(["dfs", "bellman-ford"]), default="dfs", help="Алгоритм поиска")
@click.option("--processes", type=int, default=None, help="Количество рабочих процессов")
@click.option("--prune-ratio", type=float, default=0.0, help="Коэффициент отсечения нерентабельных веток")
@click.option("--batch-size", type=int, default=20, help="Размер батча при загрузке книг ордеров")
@click.option("--historical-prices", help="Исторические цены через запятую для прогнозирования")
@click.option("--auto-fetch-history", is_flag=True, help="Автоматически получить исторические данные с биржи")
@click.option("--history-hours", type=int, default=24, help="Количество часов истории для загрузки")
@click.option("--history-symbol", help="Торговая пара для исторических данных (например, BTC/USDT)")
@click.option("--forecast-method", type=click.Choice(["mean", "median", "ema", "arima"]), default="mean", help="Метод прогнозирования")
@click.option("--forecast-horizon", type=int, default=5, help="Горизонт прогнозирования (в минутах)")
@click.option("--lookback", type=int, default=60, help="Окно для анализа исторических данных")
def forecast_arbitrage(
    ctx,
    max_depth,
    start,
    amount,
    cached,
    cache_dir,
    exchange_list,
    algorithm,
    processes,
    prune_ratio,
    batch_size,
    historical_prices,
    auto_fetch_history,
    history_hours,
    history_symbol,
    forecast_method,
    forecast_horizon,
    lookback,
) -> None:
    """
    Найти арбитражные возможности с интегрированным прогнозированием.
    
    Эта команда объединяет поиск арбитража с анализом рыночных трендов:
    
    **Что делает:**
    1. Находит арбитражные возможности между биржами
    2. Анализирует исторические данные для прогнозирования
    3. Делает прогнозы движения цен
    4. Рекомендует действия на основе прогнозов и прибыльности
    
    **Методы прогнозирования:**
    - mean: Среднее значение доходностей
    - median: Медианное значение доходностей
    - ema: Экспоненциальное скользящее среднее
    - arima: Авторегрессионная модель
    
    **Рекомендации:**
    - buy: Рекомендуется покупать (ожидается рост + хорошая прибыль)
    - sell: Рекомендуется продавать (ожидается падение)
    - hold: Рекомендуется держать (неопределенный тренд)
    
    **Примеры:**
        python -m cthulhu_src.main forecast-arbitrage -s binance_BTC -a 0.001
        python -m cthulhu_src.main forecast-arbitrage -s binance_BTC --historical-prices 50000,50100,50200,50300
        python -m cthulhu_src.main forecast-arbitrage -s binance_BTC --auto-fetch-history
        python -m cthulhu_src.main forecast-arbitrage -s binance_BTC --auto-fetch-history --history-hours 48
        python -m cthulhu_src.main forecast-arbitrage -s binance_BTC --forecast-method arima --forecast-horizon 10
    """
    
    # Парсим исторические цены если предоставлены
    historical_prices_list = None
    if historical_prices:
        try:
            historical_prices_list = [float(p.strip()) for p in historical_prices.split(",") if p.strip()]
        except ValueError:
            click.echo("❌ Ошибка: исторические цены должны быть числами, разделенными запятыми")
            return
    
    asyncio.run(
        run_cmd(
            ctx,
            max_depth,
            exchange_list,
            start,
            amount,
            cache_dir,
            historical_prices_list,
            forecast_method,
            forecast_horizon,
            lookback,
            auto_fetch_history,
            history_hours,
            history_symbol,
            cached,
            algorithm,
            processes,
            prune_ratio,
            batch_size,
            (),
        )
    ) 