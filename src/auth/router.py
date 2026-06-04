from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from src.auth.schemas import UserCreate, UserLogin, UserResponse, UserAdminUpdate, ForgotPasswordRequest, ResetPasswordRequest
from src.auth import service
from src.auth.utils import create_access_token, create_refresh_token, decode_refresh_token
from src.config import settings
from src.auth.dependencies import admin_required
from typing import List

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse)
async def register(user_in: UserCreate):
    return await service.register_user(user_in)

@router.post("/login")
async def login(user_in: UserLogin, response: Response):
    user = await service.authenticate_user(user_in.username, user_in.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tài khoản hoặc mật khẩu không chính xác",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 1. Tạo JWT Access Token và Refresh Token
    access_token = create_access_token(str(user.id), user.username)
    refresh_token = create_refresh_token(str(user.id))
    
    # 2. Lưu trữ Refresh Token vào MongoDB để quản lý trạng thái phiên
    await service.store_refresh_token(str(user.id), refresh_token)
    
    # 3. Đặt Cookies bảo mật
    response.set_cookie(
        key="access_token",
        value=access_token,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        httponly=False,  # Client JS có thể dùng Authorization header từ cookie này
        secure=True,
        samesite="lax"
    )
    
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        httponly=True,   # Ngăn chặn XSS truy cập token
        secure=True,
        samesite="lax",
        path="/api/v1/auth"  # Chỉ gửi khi gọi các endpoints liên quan tới auth
    )
    
    return {
        "message": "Đăng nhập thành công",
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": {
            "id": str(user.id),
            "username": user.username,
            "email": user.email
        }
    }

@router.post("/refresh")
async def refresh_tokens(request: Request, response: Response):
    # 1. Trích xuất Refresh Token từ Cookie hoặc Header (dự phòng)
    refresh_token = request.cookies.get("refresh_token")
    
    if not refresh_token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            refresh_token = auth_header.split(" ")[1]
            
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Không tìm thấy Refresh Token. Vui lòng đăng nhập lại."
        )
        
    # 2. Xác thực cấu trúc và chữ ký token
    payload = decode_refresh_token(refresh_token)
    user_id = payload.get("sub")
    
    # 3. Kiểm tra xem token này đã bị thu hồi trong database chưa
    is_valid = await service.verify_stored_refresh_token(refresh_token)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Phiên làm việc đã hết hạn hoặc token đã bị vô hiệu hóa"
        )
        
    # 4. Thu hồi Refresh Token cũ (Refresh Token Rotation)
    await service.revoke_refresh_token(refresh_token)
    
    # 5. Tạo cặp Access Token và Refresh Token mới
    access_token = create_access_token(user_id, "")
    new_refresh_token = create_refresh_token(user_id)
    
    # 6. Ghi nhận Refresh Token mới vào database
    await service.store_refresh_token(user_id, new_refresh_token)
    
    # 7. Đặt cookies cập nhật mới
    response.set_cookie(
        key="access_token",
        value=access_token,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        httponly=False,
        secure=True,
        samesite="lax"
    )
    
    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        httponly=True,
        secure=True,
        samesite="lax",
        path="/api/v1/auth"
    )
    
    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token
    }

@router.post("/logout")
async def logout(request: Request, response: Response):
    refresh_token = request.cookies.get("refresh_token")
    if refresh_token:
        # Vô hiệu hóa token trong database
        await service.revoke_refresh_token(refresh_token)
        
    # Xóa cookies trên trình duyệt
    response.delete_cookie(key="access_token", secure=True, samesite="lax")
    response.delete_cookie(key="refresh_token", path="/api/v1/auth", secure=True, samesite="lax")
    
    return {"message": "Đăng xuất thành công"}

@router.post("/forgot-password")
async def forgot_password(payload: ForgotPasswordRequest):
    await service.generate_and_send_otp(payload.email)
    return {"message": "Mã OTP đặt lại mật khẩu đã được gửi đến email của bạn"}

@router.post("/reset-password")
async def reset_password(payload: ResetPasswordRequest):
    await service.verify_otp_and_reset_password(
        email=payload.email,
        otp=payload.otp,
        new_password=payload.new_password
    )
    return {"message": "Đặt lại mật khẩu thành công. Vui lòng đăng nhập bằng mật khẩu mới."}

# QUẢN TRỊ NGƯỜI DÙNG (ADMIN ENDPOINTS)

@router.get("/users", response_model=List[UserResponse], tags=["User Management"])
async def list_users(current_admin = Depends(admin_required)):
    """
    [Admin Only] Lấy danh sách toàn bộ tài khoản người dùng trong hệ thống.
    """
    return await service.get_all_users()

@router.patch("/users/{user_id}", response_model=UserResponse, tags=["User Management"])
async def update_user(
    user_id: str,
    update_in: UserAdminUpdate,
    current_admin = Depends(admin_required)
):
    """
    [Admin Only] Khóa/mở khóa tài khoản (is_active) hoặc thay đổi quyền (role) của người dùng khác.
    """
    # Ngăn chặn Admin tự khóa hoặc hạ quyền của chính mình
    if str(current_admin.id) == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bạn không thể tự thay đổi quyền hoặc khóa tài khoản của chính mình"
        )
        
    updated_user = await service.update_user_by_admin(
        user_id=user_id,
        role=update_in.role,
        is_active=update_in.is_active
    )
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy người dùng cần cập nhật"
        )
    return updated_user

