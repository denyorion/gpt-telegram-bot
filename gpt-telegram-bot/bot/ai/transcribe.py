"""Voice-to-text transcription using Google Gemini (google-genai v2026)."""
import logging

from google import genai
from google.genai import types

from bot.config import GOOGLE_API_KEY, LLM_MODEL

logger = logging.getLogger(__name__)

client = genai.Client(api_key=GOOGLE_API_KEY)


async def transcribe_audio(audio_bytes: bytes, filename: str = "voice.ogg") -> str:
    """
    Transcribes audio using Gemini native multimodal capabilities.
    Telegram voice messages are typically OGG/Opus.
    """
    try:
        response = await client.aio.models.generate_content(
            model=LLM_MODEL,
            contents=[
                "Transcribe this voice message to text. Output only transcribed text.",
                types.Part.from_bytes(data=audio_bytes, mime_type="audio/ogg"),
            ],
        )
        if response and response.text:
            return response.text.strip()
        return "Не удалось распознать аудио."
    except Exception as e:
        logger.error("Transcription error: %s", e)
        if "429" in str(e) or "resource_exhausted" in str(e).lower():
            return "Слишком много запросов. Подожди минуту и попробуй снова."
        return "Не удалось распознать аудио."
