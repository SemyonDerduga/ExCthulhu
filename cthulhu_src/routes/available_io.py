import click

from cthulhu_src.actions.available_io import run as run_cmd

"""
    Command for getting currencies available for input and output for exchange.
"""


@click.command()
@click.pass_context
@click.argument("exchange")
def available_io(ctx, exchange) -> None:
    """
    Получить список валют, доступных для ввода и вывода на бирже.
    
    Эта команда проверяет, какие криптовалюты можно пополнить и вывести
    с указанной биржи. Результаты сохраняются в файлы:
    ~/.cache/cthulhu/available_io/{exchange}_input.txt
    ~/.cache/cthulhu/available_io/{exchange}_output.txt
    
    Поддерживаемые биржи: binance, exmo, hollaex, oceanex, 
    poloniex, upbit, yobit
    
    Примеры:
        python -m cthulhu_src.main available-io binance
        python -m cthulhu_src.main available-io hollaex
        python -m cthulhu_src.main available-io yobit
    """
    run_cmd(ctx, exchange)
