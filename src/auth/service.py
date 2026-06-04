from src.database import get_db
from src.auth.models import User
from src.auth.schemas import UserCreate
from src.auth.utils import hash_password, verify_password
from src.config import settings
from fastapi import HTTPException, status
import time
import random
import smtplib
import asyncio
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional
from bson import ObjectId
from bson.errors import InvalidId

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

# QUẢN TRỊ NGƯỜI DÙNG (ADMIN SERVICES)

async def get_all_users() -> List[User]:
    """
    Lấy danh sách toàn bộ người dùng trong hệ thống
    """
    db = await get_db()
    cursor = db["users"].find()
    users = await cursor.to_list(length=1000)
    return [User(**u) for u in users]

async def update_user_by_admin(
    user_id: str, 
    role: Optional[str] = None, 
    is_active: Optional[bool] = None
) -> Optional[User]:
    """
    Cập nhật vai trò hoặc trạng thái hoạt động của người dùng khác
    """
    db = await get_db()
    try:
        obj_id = ObjectId(user_id)
    except (InvalidId, TypeError):
        return None

    update_data = {}
    if role is not None:
        update_data["role"] = role
    if is_active is not None:
        update_data["is_active"] = is_active

    if update_data:
        await db["users"].update_one({"_id": obj_id}, {"$set": update_data})

    user_dict = await db["users"].find_one({"_id": obj_id})
    if not user_dict:
        return None
    return User(**user_dict)


# XỬ LÝ GỬI EMAIL OTP VÀ QUÊN MẬT KHẨU (OTP & PASSWORD RESET SERVICES)

def send_smtp_email_sync(to_email: str, subject: str, html_content: str):
    """
    Sends an email using standard smtplib (synchronous blocking network call).
    """
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = settings.SMTP_USER
    msg["To"] = to_email
    
    part = MIMEText(html_content, "html", "utf-8")
    msg.attach(part)
    
    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
         server.starttls()
         server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
         server.sendmail(settings.SMTP_USER, to_email, msg.as_string())

async def send_smtp_email(to_email: str, subject: str, html_content: str):
    """
    Wraps the synchronous SMTP sending in an async executor to prevent blocking.
    """
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, send_smtp_email_sync, to_email, subject, html_content)

async def generate_and_send_otp(email: str):
    """
    Generates a 6-digit OTP, stores it in MongoDB, and sends it to the user's email.
    """
    db = await get_db()
    
    # Verify user exists
    user = await db["users"].find_one({"email": email})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy tài khoản liên kết với email này"
        )
        
    # Generate 6-digit numeric code
    otp = "".join([str(random.randint(0, 9)) for _ in range(6)])
    
    # Store OTP in DB
    await db["otps"].insert_one({
        "email": email,
        "otp": otp,
        "is_used": False,
        "expires_at": time.time() + 300  # Valid for 5 minutes
    })
    
    # Render HTML template
    html_content = f"""
    <html>
      <body style="font-family: sans-serif; color: #37352f; padding: 20px; max-width: 600px; margin: 0 auto; border: 1px solid #efefed; border-radius: 8px;">
        <h2 style="color: #2383e2; margin-bottom: 20px;">Yêu cầu đặt lại mật khẩu - Aura Book</h2>
        <p>Xin chào,</p>
        <p>Chúng tôi đã nhận được yêu cầu đặt lại mật khẩu cho tài khoản Aura Book của bạn. Dưới đây là mã xác thực OTP của bạn:</p>
        <div style="background: #fbfbfa; border: 1px solid #efefed; border-radius: 6px; padding: 15px 30px; display: inline-block; margin: 20px 0;">
          <span style="font-size: 32px; font-weight: 700; font-family: monospace; letter-spacing: 4px; color: #2383e2;">{otp}</span>
        </div>
        <p style="color: #7c7b77; font-size: 13px;">Mã này chỉ có hiệu lực trong vòng 5 phút. Vui lòng tuyệt đối không chia sẻ mã này với bất kỳ ai.</p>
        <hr style="border: none; border-top: 1px solid #efefed; margin: 25px 0;">
        <p style="font-size: 12px; color: #acaba9;">Email này được gửi tự động từ hệ thống Aura Book. Vui lòng không trả lời trực tiếp email này.</p>
      </body>
    </html>
    """
    
    # Send email
    try:
        await send_smtp_email(email, "Mã xác thực đặt lại mật khẩu Aura Book", html_content)
    except Exception as e:
        # Log error
        print(f"SMTP error sending OTP email: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể gửi email OTP đặt lại mật khẩu. Vui lòng kiểm tra cấu hình SMTP."
        )

async def verify_otp_and_reset_password(email: str, otp: str, new_password: str):
    """
    Verifies that the OTP is correct and unexpired, then updates the user's password.
    """
    db = await get_db()
    
    # Find valid unexpired unused OTP
    otp_record = await db["otps"].find_one({
        "email": email,
        "otp": otp,
        "is_used": False,
        "expires_at": {"$gt": time.time()}
    })
    
    if not otp_record:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mã OTP không chính xác hoặc đã hết hạn"
        )
        
    # Mark OTP as used
    await db["otps"].update_one(
        {"_id": otp_record["_id"]},
        {"$set": {"is_used": True}}
    )
    
    # Hash new password
    hashed_pw = hash_password(new_password)
    
    # Update user's password
    await db["users"].update_one(
        {"email": email},
        {"$set": {"hashed_password": hashed_pw}}
    )

