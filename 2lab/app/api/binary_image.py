from fastapi import APIRouter, HTTPException
from app.schemas.binary import BinaryImageRequest, BinaryImageResponse
import base64
import cv2
import numpy as np

router = APIRouter()


@router.post("/binary_image", response_model=BinaryImageResponse)
def binary_image_endpoint(data: BinaryImageRequest):
    try:
        image_bytes = base64.b64decode(data.image)
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
        if img is None:
            raise ValueError("Не удалось декодировать изображение")
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid image data")

    algorithm = data.algorithm.lower()
    if algorithm == "otsu":
        _, img_thresh = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    else:
        raise HTTPException(status_code=400, detail="Unsupported algorithm")

    ret, buffer = cv2.imencode('.png', img_thresh)
    if not ret:
        raise HTTPException(status_code=500, detail="Image encoding failed")
    bin_image_base64 = base64.b64encode(buffer).decode('utf-8')

    return {"binarized_image": bin_image_base64}