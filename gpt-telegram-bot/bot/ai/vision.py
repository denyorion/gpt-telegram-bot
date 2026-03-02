"""Image analysis via Google Gemini (OCR, scene description)."""
import asyncio
import base64
import random
import time

import google.generativeai as genai

from bot.config import GOOGLE_API_KEY, VISION_MODEL

genai.configure(api_key=GOOGLE_API_KEY)


def _media_type(image_bytes: bytes) -> str:
    if image_bytes[:8].startswith(b"\x89PNG"):
        return "image/png"
    if image_bytes[:4] == b"RIFF" and image_bytes[8:12] == b"WEBP":
        return "image/webp"
    return "image/jpeg"


def _is_rate_limit_error(exc: Exception) -> bool:
    msg = str(exc)
    name = exc.__class__.__name__.lower()
    return (
        "429" in msg
        or "resource_exhausted" in msg.lower()
        or "too many requests" in msg.lower()
        or "ratelimit" in name
        or "toomanyrequests" in name
        or "resourceexhausted" in name
    )


def _analyze_image_sync(
    image_bytes: bytes,
    user_prompt: str = "",
    model_name: str = VISION_MODEL,
) -> str:
    """Sync: send image to Gemini Vision."""
    mime = _media_type(image_bytes)
    b64 = base64.standard_b64encode(image_bytes).decode("utf-8")
    model = genai.GenerativeModel(model_name)
    parts = []
    if user_prompt:
        parts.append(user_prompt)
    parts.append({"inline_data": {"mime_type": mime, "data": b64}})
    max_retries = 3
    for attempt in range(max_retries + 1):
        try:
            response = model.generate_content(
                parts,
                generation_config={"max_output_tokens": 1024},
            )
            return (response.text or "").strip()
        except Exception as e:
            if _is_rate_limit_error(e):
                if attempt < max_retries:
                    backoff = min(60.0, (2**attempt) + random.random())
                    time.sleep(backoff)
                    continue
                return (
                    "Сейчас слишком много запросов к Gemini Vision (лимит). "
                    "Пожалуйста, подожди минуту и попробуй снова."
                )
            raise


async def analyze_image(
    image_bytes: bytes,
    user_prompt: str = "",
    model: str = VISION_MODEL,
) -> str:
    """Send image to Gemini Vision. user_prompt can be caption or question."""
    return await asyncio.to_thread(
        _analyze_image_sync, image_bytes, user_prompt, model
    )
