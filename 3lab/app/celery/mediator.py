from redislite import Redis
import json
import threading

class WebSocketMediator:
    def __init__(self, db_path='/tmp/websocket_redis.db'):
        self.redis = Redis(db_path)
        self.pubsub = self.redis.pubsub()
        self._lock = threading.Lock()

    def send_to_websocket(self, channel: str, message: dict):
        with self._lock:
            self.redis.publish(f"ws_{channel}", json.dumps(message))

    def register_celery_task(self, task_id: str, data: dict):
        with self._lock:
            self.redis.hset("celery_tasks", task_id, json.dumps(data))

    def get_celery_task(self, task_id: str) -> dict:
        data = self.redis.hget("celery_tasks", task_id)
        return json.loads(data) if data else None

    def close(self):
        self.redis.shutdown()