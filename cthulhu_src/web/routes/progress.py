"""
Маршруты для отслеживания прогресса операций.
"""

import asyncio
import json
import logging
from typing import Any, Dict

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

logger = logging.getLogger("excthulhu")

router = APIRouter()

# Глобальное хранилище прогресса (в продакшене лучше использовать Redis)
_progress_store: Dict[str, Dict[str, Any]] = {}


def update_progress(task_id: str, progress: int, message: str, stage: str = "general"):
    """Обновить прогресс задачи."""
    if task_id not in _progress_store:
        _progress_store[task_id] = {}

    _progress_store[task_id].update(
        {
            "progress": progress,
            "message": message,
            "stage": stage,
            "timestamp": asyncio.get_event_loop().time(),
        }
    )

    logger.info(f"Прогресс {task_id}: {progress}% - {message}")
    logger.info(f"Хранилище прогресса: {_progress_store}")


def get_progress(task_id: str) -> Dict[str, Any]:
    """Получить текущий прогресс задачи."""
    return _progress_store.get(
        task_id,
        {
            "progress": 0,
            "message": "Задача не найдена",
            "stage": "unknown",
            "timestamp": 0,
        },
    )


@router.get("/progress/{task_id}")
async def get_task_progress(task_id: str):
    """Получить прогресс задачи."""
    return get_progress(task_id)


@router.get("/progress-stream/{task_id}")
async def progress_stream(task_id: str):
    """Потоковый API для отслеживания прогресса в реальном времени."""

    logger.info(f"SSE подключение для задачи {task_id}")

    async def event_stream():
        last_progress = -1

        while True:
            progress_data = get_progress(task_id)
            current_progress = progress_data.get("progress", 0)

            # Отправляем обновления только при изменении прогресса
            if current_progress != last_progress:
                message = f"data: {json.dumps(progress_data)}\n\n"
                logger.info(f"SSE отправка для {task_id}: {current_progress}%")
                yield message
                last_progress = current_progress

            # Если задача завершена (100%), прекращаем поток
            if current_progress >= 100:
                message = (
                    f"data: {json.dumps({**progress_data, 'completed': True})}\n\n"
                )
                logger.info(f"SSE завершение для {task_id}")
                yield message
                break

            await asyncio.sleep(0.5)  # Обновляем каждые 500мс

    return StreamingResponse(
        event_stream(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream",
        },
    )
