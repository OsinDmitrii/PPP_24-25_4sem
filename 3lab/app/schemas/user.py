from pydantic import BaseModel, EmailStr, ConfigDict

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserOut(UserBase):
    id: int
    model_config = ConfigDict(from_attributes=True)      #   UPDATED FOR NEW VERSION
                                                         #   TO DELETE

class UserResponse(UserOut):
    token: str