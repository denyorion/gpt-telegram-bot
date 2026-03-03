"""Async Gemini API via google-genai (v2026) SDK."""
import logging

from google import genai

from bot.config import GOOGLE_API_KEY, LLM_MODEL

logger = logging.getLogger(__name__)

# Single client instance for the whole bot
client = genai.Client(api_key=GOOGLE_API_KEY)


async def get_gemini_response(prompt: str, image_data: dict | None = None) -> str:
    """
    Sends a request to Gemini using the latest SDK (async).
    Supports both text and multimodal (image) inputs.
    """
    try:
        content_parts: list = [prompt]

        if image_data:
            # image_data: {"mime_type": "image/jpeg", "data": bytes}
            content_parts.append(image_data)

        response = await client.aio.models.generate_content(
            model=LLM_MODEL,
            contents=content_parts,
        )

        if response and response.text:
            return response.text.strip()
        return "⚠️ AI вернул пустой ответ."

    except Exception as e:
        logger.error("Gemini API Error: %s", e)
        if "429" in str(e) or "resource_exhausted" in str(e).lower():
            return (
                "🕒 Достигнут лимит запросов. Подожди около минуты и попробуй снова."
            )
        return "❌ Ошибка при обработке запроса."
