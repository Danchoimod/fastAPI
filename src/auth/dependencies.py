from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from src.auth.utils import decode_access_token
from src.auth.models import User
from src.database import get_db
from bson import ObjectId

# Supports Bearer tokens via HTTP headers
security = HTTPBearer(auto_error=False)

async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    token = None
    
    # 1. Try to extract token from Authorization header (Bearer token)
    if credentials:
        token = credentials.credentials
        
    # 2. Sách lược dự phòng: Trích xuất token từ Cookie
    if not token:
        token = request.cookies.get("access_token")
        
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Chưa xác thực người dùng",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    # Giải mã và xác minh tính hợp lệ của Access Token
    payload = decode_access_token(token)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Mã xác thực không hợp lệ",
        )
        
    # Tìm kiếm người dùng tương ứng trong cơ sở dữ liệu
    db = await get_db()
    try:
        user_dict = await db["users"].find_one({"_id": ObjectId(user_id)})
    except Exception:
        user_dict = None
        
    if not user_dict:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Không tìm thấy người dùng",
        )
        
    return User(**user_dict)

async def admin_required(current_user: User = Depends(get_current_user)):
    role = getattr(current_user, "role", "USER")
    if role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Bạn không có quyền Admin"
        )
    return current_user