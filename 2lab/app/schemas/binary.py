from pydantic import BaseModel

class BinaryImageRequest(BaseModel):
    image: str        
    algorithm: str

class BinaryImageResponse(BaseModel):
    binarized_image: str