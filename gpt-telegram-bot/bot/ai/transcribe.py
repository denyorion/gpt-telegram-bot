"""Voice-to-text transcription using Google Gemini (google-genai v2026)."""
import logging

from bot.ai.ai_service import client
from bot.config import LLM_MODEL

logger = logging.getLogger(__name__)


async def transcribe_audio(audio_bytes: bytes, filename: str = "voice.ogg") -> str:
    """
    Transcribes audio using Gemini native multimodal capabilities.
    Telegram voice messages are typically OGG/Opus.
    """
    try:
        response = await client.aio.models.generate_content(
            model=LLM_MODEL,
            contents=[
                "Transcribe this voice message to plain text. Reply only with the transcription, no extra commentary. Keep the same language as the speaker.",
                {"mime_type": "audio/ogg", "data": audio_bytes},
            ],
        )
        if response and response.text:
            return response.text.strip()
        return "Не удалось распознать аудио."
    except Exception as e:
        logger.error("Transcription error: %s", e)
        if "429" in str(e) or "resource_exhausted" in str(e).lower():
            return "Слишком много запросов. Подожди минуту и попробуй снова."
        return "Ошибка распознавания аудио."
