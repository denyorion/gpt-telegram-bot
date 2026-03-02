"""Voice-to-text transcription using Google Gemini (audio understanding)."""
import asyncio
import tempfile
from pathlib import Path

import google.generativeai as genai

from bot.config import GOOGLE_API_KEY, LLM_MODEL

genai.configure(api_key=GOOGLE_API_KEY)


def _transcribe_sync(audio_bytes: bytes, filename: str) -> str:
    """Sync transcription: send audio to Gemini and ask for text."""
    with tempfile.NamedTemporaryFile(
        suffix=Path(filename).suffix or ".ogg", delete=False
    ) as f:
        f.write(audio_bytes)
        path = f.name
    try:
        audio_file = genai.upload_file(path, mime_type="audio/ogg")
        model = genai.GenerativeModel(LLM_MODEL)
        response = model.generate_content(
            [
                "Transcribe this voice message to plain text. Reply only with the transcription, no extra commentary. Keep the same language as the speaker.",
                audio_file,
            ]
        )
        return (response.text or "").strip()
    finally:
        Path(path).unlink(missing_ok=True)


async def transcribe_audio(audio_bytes: bytes, filename: str = "voice.ogg") -> str:
    """Transcribe voice message with Gemini. Telegram sends OGG/Opus."""
    return await asyncio.to_thread(_transcribe_sync, audio_bytes, filename)
