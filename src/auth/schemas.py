from pydantic import BaseModel, EmailStr
from typing import Optional

class UserBase(BaseModel):
    username: str
    email: EmailStr
    role: Optional[str] = "USER"

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

class UserAdminUpdate(BaseModel):
    role: Optional[str] = None
    is_active: Optional[bool] = None

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    email: EmailStr
    otp: str
    new_password: str


