"""
Маршруты для HTML страниц.
"""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

import os

templates_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")
templates = Jinja2Templates(directory=templates_dir)
router = APIRouter()


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Страница дашборда."""
    return templates.TemplateResponse("dashboard.html", {"request": request})


@router.get("/arbitrage", response_class=HTMLResponse)
async def arbitrage_page(request: Request):
    """Страница поиска арбитража."""
    return templates.TemplateResponse("arbitrage.html", {"request": request})


@router.get("/forecast", response_class=HTMLResponse)
async def forecast_page(request: Request):
    """Страница прогнозирования."""
    return templates.TemplateResponse("forecast.html", {"request": request})


@router.get("/historical", response_class=HTMLResponse)
async def historical_page(request: Request):
    """Страница исторических данных."""
    return templates.TemplateResponse("historical.html", {"request": request})


@router.get("/integrated", response_class=HTMLResponse)
async def integrated_page(request: Request):
    """Страница интегрированного анализа."""
    return templates.TemplateResponse("integrated.html", {"request": request})


@router.get("/test", response_class=HTMLResponse)
async def test_page(request: Request):
    """Страница тестирования API."""
    return templates.TemplateResponse("test_api.html", {"request": request})
