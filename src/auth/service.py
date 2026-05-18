from src.database import get_db
from src.auth.models import User
from src.auth.schemas import UserCreate
from src.auth.utils import hash_password, verify_password
from fastapi import HTTPException, status
import time

# CÁC DỊCH VỤ NGHIỆP VỤ CHÍNH (USER SERVICES)

async def register_user(user_in: UserCreate):
    db = await get_db()
    
    # Check if user already exists
    existing_user = await db["users"].find_one({"$or": [{"username": user_in.username}, {"email": user_in.email}]})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered"
        )
    
    # Hash password and create user object
    hashed_pw = hash_password(user_in.password)
    user_dict = user_in.model_dump()
    user_dict.pop("password")
    user_dict["hashed_password"] = hashed_pw
    user_dict["is_active"] = True
    
    # Insert into DB
    result = await db["users"].insert_one(user_dict)
    user_dict["_id"] = result.inserted_id
    
    return User(**user_dict)

async def authenticate_user(username: str, password: str):
    db = await get_db()
    user = await db["users"].find_one({"username": username})
    if not user:
        return None
    
    if not verify_password(password, user["hashed_password"]):
        return None
    
    return User(**user)

# QUẢN LÝ REFRESH TOKEN (REFRESH TOKEN SERVICES)

async def store_refresh_token(user_id: str, token: str):
    """
    Lưu trữ Refresh Token mới vào MongoDB collection 'refresh_tokens'
    """
    db = await get_db()
    await db["refresh_tokens"].insert_one({
        "user_id": user_id,
        "token": token,
        "is_revoked": False,
        "created_at": time.time()
    })

async def revoke_refresh_token(token: str):
    """
    Thu hồi (revoke) một Refresh Token trong MongoDB
    """
    db = await get_db()
    await db["refresh_tokens"].update_many(
        {"token": token},
        {"$set": {"is_revoked": True}}
    )

async def verify_stored_refresh_token(token: str) -> bool:
    """
    Kiểm tra xem Refresh Token có hợp lệ trong database và chưa bị thu hồi hay không
    """
    db = await get_db()
    stored = await db["refresh_tokens"].find_one({"token": token, "is_revoked": False})
    return stored is not None
