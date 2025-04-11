from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from app.core.config import SECRET_KEY, ALGORITHM
from app.db.database import get_db
from sqlalchemy.orm import Session
from app.models.user import User

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
         status_code=status.HTTP_401_UNAUTHORIZED,
         detail="Could not validate credentials",
         headers={"WWW-Authenticate": "Bearer"},
    )
    try:
         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
         email: str = payload.get("sub")
         if email is None:
             raise credentials_exception
    except JWTError:
         raise credentials_exception
    user = db.query(User).filter(User.email == email).first()
    if user is None:
         raise credentials_exception
    return user

@router.get("/users/me/", response_model=dict)
def read_users_me(current_user: User = Depends(get_current_user)):
    return {"id": current_user.id, "email": current_user.email}