import click

from cthulhu_src.actions.config import run as run_cmd

"""
    Команда для поиска прибыльных транзакций с настройками из конфигурационного файла.
"""


@click.command()
@click.pass_context
@click.argument("config", type=click.Path(exists=True))
def config(ctx, config) -> None:
    """
    Найти прибыльные транзакции используя настройки из конфигурационного файла.
    
    Эта команда позволяет запускать поиск арбитража с предварительно
    сохраненными настройками в JSON или YAML файле.
    
    Примеры:
        python -m cthulhu_src.main config config.yaml
        python -m cthulhu_src.main config settings.json
    """
    run_cmd(ctx, config)
