import click
import asyncio
from cthulhu_src.actions.historical_data import run as run_cmd

"""
    Команда для получения исторических данных с бирж.
"""


@click.command()
@click.pass_context
@click.argument("exchange")
@click.argument("symbol")
@click.option("--hours", type=int, default=24, help="Количество часов истории")
@click.option("--count", type=int, default=100, help="Количество последних записей")
@click.option("--format", type=click.Choice(["prices", "ohlcv", "info"]), default="prices", help="Формат вывода")
def historical_data(ctx, exchange: str, symbol: str, hours: int, count: int, format: str) -> None:
    """
    Получить исторические данные с биржи.
    
    Эта команда позволяет получать различные типы исторических данных:
    
    **Форматы вывода:**
    - prices: Только цены закрытия (для прогнозирования)
    - ohlcv: Полные OHLCV данные (Open, High, Low, Close, Volume)
    - info: Информация о рынке (текущие цены, объемы, изменения)
    
    **Примеры:**
        python -m cthulhu_src.main historical-data binance BTC/USDT
        python -m cthulhu_src.main historical-data binance BTC/USDT --hours 48
        python -m cthulhu_src.main historical-data binance BTC/USDT --format ohlcv
        python -m cthulhu_src.main historical-data binance BTC/USDT --format info
    """
    asyncio.run(run_cmd(ctx, exchange, symbol, hours, count, format)) 