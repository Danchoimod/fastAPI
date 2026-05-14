from fastapi import APIRouter, Depends, HTTPException, status
from src.auth.schemas import UserCreate, UserLogin, UserResponse
from src.auth import service

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse)
async def register(user_in: UserCreate):
    return await service.register_user(user_in)

@router.post("/login")
async def login(user_in: UserLogin):
    user = await service.authenticate_user(user_in.username, user_in.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
            #thiết lập login bằng cookie
        )
    return {"message": "Login successful", "user": user.username}
