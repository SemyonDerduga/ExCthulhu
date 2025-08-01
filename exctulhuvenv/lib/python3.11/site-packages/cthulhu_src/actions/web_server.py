"""
Действие для запуска веб-сервера.
"""

import logging
from cthulhu_src.web.app import run_web_server

logger = logging.getLogger("excthulhu")


def run(
    ctx,
    host: str = "0.0.0.0",
    port: int = 8000,
    reload: bool = True,
) -> None:
    """
    Запустить веб-сервер.
    
    Args:
        ctx: Контекст CLI
        host: Хост для запуска сервера
        port: Порт для запуска сервера
        reload: Автоматическая перезагрузка при изменениях
    """
    logger.info(f"🚀 Запускаем веб-сервер на http://{host}:{port}")
    logger.info("📊 Веб-интерфейс будет доступен в браузере")
    logger.info("🛑 Для остановки нажмите Ctrl+C")
    
    try:
        run_web_server(host=host, port=port, reload=reload)
    except KeyboardInterrupt:
        logger.info("👋 Веб-сервер остановлен")
    except Exception as e:
        logger.error(f"❌ Ошибка запуска веб-сервера: {e}")
        raise 