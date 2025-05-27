# main.py
import os
from fastapi import FastAPI
import uvicorn
from redislite import Redis

from app.api import auth, users, binary_image
from app.websockets import image_bin
from app.db.database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Лаб 3 – WS + Celery")

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(binary_image.router)
app.include_router(image_bin.router)


from redislite import Redis

def run_redislite() -> Redis:
    return Redis("/tmp/websocket_redis.db")

if __name__ == "__main__":
    redis_srv = run_redislite()
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)