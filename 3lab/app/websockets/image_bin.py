# app/websockets/image_bin.py
from celery_app import DB_PATH
import asyncio
import json
from threading import Thread

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from redislite import Redis

from celery_app import mediator  # только чтобы получить путь к БД
from app.celery.tasks import binarize_image  # Celery-задача

router = APIRouter(prefix="/ws", tags=["websocket"])


def _redis_listener(ws: WebSocket, user_id: int, loop):
    """Отдельный поток, слушает Redis-канал «ws_{user_id}» и прокидывает в WebSocket."""
    redis = Redis(DB_PATH)                  # стало
 # type: ignore[attr-defined]  # noqa: SLF001
    pubsub = redis.pubsub()
    pubsub.subscribe(f"ws_{user_id}")

    for message in pubsub.listen():
        if message["type"] == "message":
            try:
                payload = json.loads(message["data"])
                asyncio.run_coroutine_threadsafe(ws.send_json(payload), loop)
            except Exception:  # noqa: BLE001
                break
    pubsub.unsubscribe()
    redis.close()


@router.websocket("/{user_id}")
async def websocket_endpoint(ws: WebSocket, user_id: int):
    """
    Канал одного пользователя.

    1. Принимает JSON вида `{"image": "...base64...", "algorithm": "otsu"}`.
    2. Кладёт задачу в Celery.
    3. Асинхронно стримит назад STARTED / PROGRESS / COMPLETED.
    """
    await ws.accept()
    loop = asyncio.get_event_loop()

    # ── поток-слушатель Redis
    listener = Thread(target=_redis_listener, args=(ws, user_id, loop), daemon=True)
    listener.start()

    try:
        while True:
            client_data = await ws.receive_json()
            task = binarize_image.delay(user_id, client_data["image"], client_data.get("algorithm", "otsu"))
            # скажем клиенту, что задание принято
            await ws.send_json({"status": "ACCEPTED", "task_id": task.id})
    except WebSocketDisconnect:
        pass
    finally:
        listener.join(timeout=1)