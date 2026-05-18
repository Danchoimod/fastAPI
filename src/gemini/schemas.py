from pydantic import BaseModel
from typing import Optional

class GeminiChatRequest(BaseModel):
    message: str
    image_base64: Optional[str] = None
    mime_type: Optional[str] = "image/jpeg"

class GeminiChatResponse(BaseModel):
    response: str
    success: bool
