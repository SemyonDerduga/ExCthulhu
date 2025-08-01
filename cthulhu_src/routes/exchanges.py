import click

from cthulhu_src.actions.exchanges import run as run_cmd

"""
    Command show exchanges list.
"""


@click.command()
@click.pass_context
def exchanges(ctx):
    """
    Показать список всех поддерживаемых бирж.
    
    Эта команда выводит полный список криптовалютных бирж,
    которые поддерживаются библиотекой ccxt и могут быть
    использованы в других командах проекта.
    
    Пример:
        python -m cthulhu_src.main exchanges
    """
    run_cmd(ctx)
