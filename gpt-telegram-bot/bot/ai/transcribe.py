"""Voice-to-text transcription using OpenAI Whisper."""
from io import BytesIO
from openai import AsyncOpenAI

from bot.config import OPENAI_API_KEY

client = AsyncOpenAI(api_key=OPENAI_API_KEY)


async def transcribe_audio(audio_bytes: bytes, filename: str = "voice.ogg") -> str:
    """Transcribe voice message with Whisper. Telegram sends OGG/Opus."""
    audio_file = BytesIO(audio_bytes)
    audio_file.name = filename
    response = await client.audio.transcriptions.create(
        model="whisper-1",
        file=audio_file,
        response_format="text",
        language=None,
    )
    return response if isinstance(response, str) else response.get("text", "")
