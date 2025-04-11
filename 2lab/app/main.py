from fastapi import FastAPI
from app.api import auth, users, binary_image
from app.db.database import engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Лаб2")


app.include_router(auth.router)
app.include_router(users.router)
app.include_router(binary_image.router)