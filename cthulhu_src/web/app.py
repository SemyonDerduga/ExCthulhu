"""
Основное FastAPI приложение для веб-интерфейса Exchange Cthulhu.
"""

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import uvicorn
import logging

from cthulhu_src.web.routes import api, pages, progress

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("excthulhu")

# Создание FastAPI приложения
app = FastAPI(
    title="Exchange Cthulhu",
    description="Веб-интерфейс для поиска арбитража и прогнозирования",
    version="1.0.0"
)

# Подключение статических файлов
import os
static_dir = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Подключение шаблонов
templates_dir = os.path.join(os.path.dirname(__file__), "templates")
templates = Jinja2Templates(directory=templates_dir)

# Подключение маршрутов
app.include_router(pages.router, prefix="")
app.include_router(api.router, prefix="/api")
app.include_router(progress.router, prefix="/api")


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Главная страница."""
    return templates.TemplateResponse("index.html", {"request": request})


def run_web_server(host: str = "0.0.0.0", port: int = 8000, reload: bool = True):
    """Запустить веб-сервер."""
    logger.info(f"🚀 Запускаем веб-сервер на http://{host}:{port}")
    uvicorn.run(
        "cthulhu_src.web.app:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )


if __name__ == "__main__":
    run_web_server() 