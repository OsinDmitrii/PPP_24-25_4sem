from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.user import UserCreate, UserResponse
from app.cruds import user as user_crud
from app.db.database import get_db
from app.core.security import create_access_token

router = APIRouter()

@router.post("/sign-up/", response_model=UserResponse)
def sign_up(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = user_crud.get_user_by_email(db, user.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    new_user = user_crud.create_user(db, user)
    access_token = create_access_token(data={"sub": new_user.email})
    return {"id": new_user.id, "email": new_user.email, "token": access_token}

from fastapi.security import OAuth2PasswordRequestForm
from app.schemas.token import Token

@router.post("/login/", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    db_user = user_crud.get_user_by_email(db, form_data.username)
    if not db_user or not user_crud.verify_password(form_data.password, db_user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    access_token = create_access_token(data={"sub": db_user.email})

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }