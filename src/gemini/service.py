import httpx
from src.config import settings
from fastapi import HTTPException, status
import logging

logger = logging.getLogger(__name__)

async def ask_gemini(message: str, image_base64: str = None, mime_type: str = "image/jpeg") -> str:
    """
    Sends a query to Google Gemini API. Supports pure text and multimodal (text + base64 image).
    """
    # 1. Setup API parameters
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{settings.GEMINI_MODEL}:generateContent"
    params = {"key": settings.GEMINI_API_KEY}
    
    # 2. Build contents payload
    parts = []
    
    # If text message prompt is provided
    if message:
        parts.append({"text": message})
        
    # If image base64 is provided
    if image_base64:
        # Standardize base64 string if it contains data prefix (e.g. data:image/png;base64,)
        clean_base64 = image_base64
        if "," in image_base64:
            parts_split = image_base64.split(",", 1)
            clean_base64 = parts_split[1]
            # Try to dynamically resolve mime type if possible
            if "data:" in parts_split[0] and ";base64" in parts_split[0]:
                mime_type = parts_split[0].split(";")[0].replace("data:", "")
        
        parts.append({
            "inlineData": {
                "mimeType": mime_type,
                "data": clean_base64
            }
        })
        
    if not parts:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message or image must be provided"
        )
        
    payload = {
        "contents": [{
            "parts": parts
        }]
    }
    
    headers = {"Content-Type": "application/json"}
    
    # 3. Call the API asynchronously
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.post(url, json=payload, params=params, headers=headers)
            
            if response.status_code != 200:
                logger.error(f"Gemini API returned error {response.status_code}: {response.text}")
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail=f"Gemini API error: {response.text}"
                )
                
            res_data = response.json()
            
            # Extract content from response
            try:
                candidates = res_data.get("candidates", [])
                if candidates:
                    content_parts = candidates[0].get("content", {}).get("parts", [])
                    if content_parts:
                        text_response = content_parts[0].get("text", "")
                        return text_response
                
                logger.error(f"Invalid response structure from Gemini API: {res_data}")
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail="Invalid response structure from Gemini API"
                )
            except (KeyError, IndexError) as err:
                logger.error(f"Error parsing Gemini response: {err}")
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail="Error parsing response from Gemini API"
                )
                
        except httpx.RequestError as exc:
            logger.error(f"HTTP request to Gemini API failed: {exc}")
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail=f"Connection to Gemini API failed: {exc}"
            )
