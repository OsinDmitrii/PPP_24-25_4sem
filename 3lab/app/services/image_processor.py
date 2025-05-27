import cv2
import base64
import numpy as np
from fastapi import HTTPException


def process_binary_image(image_base64: str, algorithm: str) -> str:
    try:
        image_bytes = base64.b64decode(image_base64)
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
        if img is None:
            raise ValueError("Image decode failed")
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid image data")

    algorithm = algorithm.lower()
    if algorithm == "otsu":
        _, img_thresh = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    else:
        raise HTTPException(status_code=400, detail="Unsupported algorithm")

    ret, buffer = cv2.imencode('.png', img_thresh)
    if not ret:
        raise HTTPException(status_code=500, detail="Image encoding failed")
    return base64.b64encode(buffer).decode('utf-8')