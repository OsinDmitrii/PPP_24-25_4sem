# celery_app.py
import json
import threading
from pathlib import Path

from celery import Celery
from redislite import Redis

class WebSocketMediator:
    """Публикует сообщения в канал `ws_{user_id}`."""

    def __init__(self, db_path: str = "/tmp/websocket_redis.db") -> None:
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._redis = Redis(db_path)
        self._lock = threading.Lock()

    def send_to_websocket(self, user_id: int | str, payload: dict) -> None:
        """Отправка JSON-сообщения во внешний мир (слушает FastAPI-WS)."""
        with self._lock:
            self._redis.publish(f"ws_{user_id}", json.dumps(payload))


mediator = WebSocketMediator()

celery_app = Celery(
    "lab_ws",
    broker="redislite:///tmp/websocket_redis.db",
    backend="redislite:///tmp/websocket_redis.db",
    include=["tasks"],  # модуль с задачами
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    task_track_started=True,
    result_extended=True,
)