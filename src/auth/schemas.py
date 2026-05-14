from pydantic import BaseModel, EmailStr
from typing import Optional

class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str
#dữ liệu đầu vào
class UserLogin(BaseModel):
    username: str
    password: str
# dữ liệu đầu ra
class UserResponse(UserBase):
    id: str
    is_active: bool

    class Config:
        from_attributes = True
