# tasks.py
import base64
import cv2
import numpy as np
from celery import states

from celery_app import celery_app as app, mediator


@app.task(bind=True, name="binarize_image")
def binarize_image(self, user_id: int, image_b64: str, algorithm: str = "otsu"):
    """
    Долгая задача бинаризации.
    Шлёт STARTED → несколько PROGRESS → COMPLETED через mediator.
    """
    task_id = self.request.id
    mediator.send_to_websocket(
        user_id, {"status": "STARTED", "task_id": task_id, "algorithm": algorithm}
    )

    try:
        img_bytes = base64.b64decode(image_b64)
        nparr = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
        if img is None:
            raise ValueError("Не удалось декодировать изображение")
    except Exception as e:  # noqa: BLE001
        mediator.send_to_websocket(user_id, {"status": "ERROR", "task_id": task_id, "detail": str(e)})
        self.update_state(state=states.FAILURE, meta={"exc": str(e)})
        raise


    if algorithm.lower() != "otsu":
        err = f"Алгоритм «{algorithm}» пока не поддерживается"
        mediator.send_to_websocket(user_id, {"status": "ERROR", "task_id": task_id, "detail": err})
        self.update_state(state=states.FAILURE, meta={"exc": err})
        raise ValueError(err)


    for pct in (25, 50, 75):
        self.update_state(state="PROGRESS", meta={"progress": pct})
        mediator.send_to_websocket(user_id, {"status": "PROGRESS", "task_id": task_id, "progress": pct})


    _, img_thresh = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    ok, buf = cv2.imencode(".png", img_thresh)
    if not ok:
        raise ValueError("cv2.imencode вернул ошибку")

    bin_img_b64 = base64.b64encode(buf).decode()
    mediator.send_to_websocket(
        user_id, {"status": "COMPLETED", "task_id": task_id, "binarized_image": bin_img_b64}
    )

    return {"len": len(bin_img_b64)}
