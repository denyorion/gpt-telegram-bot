"""Image analysis via Google Gemini (google-genai v2026)."""
from bot.ai.ai_service import get_gemini_response


def _media_type(image_bytes: bytes) -> str:
    if image_bytes[:8].startswith(b"\x89PNG"):
        return "image/png"
    if len(image_bytes) >= 12 and image_bytes[:4] == b"RIFF" and image_bytes[8:12] == b"WEBP":
        return "image/webp"
    return "image/jpeg"


async def analyze_image(
    image_bytes: bytes,
    user_prompt: str = "",
) -> str:
    """Send image to Gemini Vision. user_prompt can be caption or question."""
    prompt = user_prompt.strip() or "Опиши или проанализируй это изображение."
    mime = _media_type(image_bytes)
    image_data = {"mime_type": mime, "data": image_bytes}
    return await get_gemini_response(prompt, image_data=image_data)
