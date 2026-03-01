"""Image analysis via GPT-4o Vision (OCR, scene description)."""
import base64
from openai import AsyncOpenAI

from bot.config import OPENAI_API_KEY, VISION_MODEL

client = AsyncOpenAI(api_key=OPENAI_API_KEY)


def _media_type(image_bytes: bytes) -> str:
    if image_bytes[:8].startswith(b"\x89PNG"):
        return "image/png"
    if image_bytes[:4] == b"RIFF" and image_bytes[8:12] == b"WEBP":
        return "image/webp"
    return "image/jpeg"


async def analyze_image(
    image_bytes: bytes,
    user_prompt: str = "",
    model: str = VISION_MODEL,
) -> str:
    """Send image to GPT-4o Vision. user_prompt can be caption or question."""
    b64 = base64.standard_b64encode(image_bytes).decode("utf-8")
    media_type = _media_type(image_bytes)
    content = [
        {
            "type": "image_url",
            "image_url": {"url": f"data:{media_type};base64,{b64}"},
        }
    ]
    if user_prompt:
        content.insert(0, {"type": "text", "text": user_prompt})
    response = await client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": content}],
        max_tokens=1024,
    )
    return response.choices[0].message.content or ""
