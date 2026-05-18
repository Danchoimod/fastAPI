from fastapi import APIRouter, Depends
from src.gemini.schemas import GeminiChatRequest, GeminiChatResponse
from src.gemini import service
from src.auth.dependencies import get_current_user

router = APIRouter()

@router.post("/chat", response_model=GeminiChatResponse)
async def chat_with_gemini(
    payload: GeminiChatRequest,
    current_user = Depends(get_current_user)
):
    """
    Sends messages or base64 images to Gemini AI securely (Requires JWT token authentication).
    """
    response_text = await service.ask_gemini(
        message=payload.message,
        image_base64=payload.image_base64,
        mime_type=payload.mime_type
    )
    return GeminiChatResponse(response=response_text, success=True)
