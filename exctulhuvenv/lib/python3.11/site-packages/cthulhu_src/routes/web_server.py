import click
from cthulhu_src.actions.web_server import run as run_cmd

"""
    Команда для запуска веб-сервера.
"""


@click.command()
@click.pass_context
@click.option("--host", default="0.0.0.0", help="Хост для запуска сервера")
@click.option("--port", type=int, default=8000, help="Порт для запуска сервера")
@click.option("--no-reload", is_flag=True, help="Отключить автоматическую перезагрузку")
def web(ctx, host: str, port: int, no_reload: bool) -> None:
    """
    Запустить веб-интерфейс Exchange Cthulhu.
    
    Запускает веб-сервер с интерактивным интерфейсом для:
    - Поиска арбитражных возможностей
    - Прогнозирования движения цен
    - Визуализации данных
    - Интегрированного анализа
    
    **Возможности веб-интерфейса:**
    - Интерактивные графики с Plotly
    - Дашборд с статистикой
    - Формы для настройки параметров
    - Визуализация результатов в реальном времени
    
    **Примеры:**
        python -m cthulhu_src.main web
        python -m cthulhu_src.main web --port 8080
        python -m cthulhu_src.main web --host 127.0.0.1 --port 3000
    """
    run_cmd(ctx, host, port, not no_reload) 