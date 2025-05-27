from fastapi import FastAPI
from app.websockets import image_bin
import uvicorn


'''app = FastAPI()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message text was: {data}")


if __name__ == "__main__":
    uvicorn.run("app:app", host='127.0.0.1', port=8000, reload=True)'''


app = FastAPI()
app.include_router(image_bin.router)


if __name__ == "__main__":
    uvicorn.run("websocket_test:app", host='127.0.0.1', port=8000, reload=True)
