import json
import threading
from pathlib import Path

from celery import Celery
from redislite import Redis

DB_PATH = "/tmp/websocket_redis.db"
Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)
_redis_server = Redis(DB_PATH)

conn = _redis_server.connection_pool.connection_kwargs
if "port" in conn:                       # Linux / Windows
    REDIS_URL = f"redis://127.0.0.1:{conn['port']}/0"
else:                                    # macOS  → unix-socket
    socket_path = _redis_server.socket_file   # абсолютный путь
    REDIS_URL = f"redis+socket://{socket_path}?db=0"

print(f"[redislite] broker/backend → {REDIS_URL}")



class WebSocketMediator:
    def __init__(self, redis):
        self._redis = redis
        self._lock = threading.Lock()

    def send_to_websocket(self, user_id, payload: dict):
        with self._lock:
            self._redis.publish(f"ws_{user_id}", json.dumps(payload))


mediator = WebSocketMediator(_redis_server)

celery_app = Celery(
    "lab_ws",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["app.celery.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    task_track_started=True,
    result_extended=True,
)
