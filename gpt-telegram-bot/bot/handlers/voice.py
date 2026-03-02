"""Handle voice messages: download and transcribe with Whisper."""
import io
from telegram import Update
from telegram.ext import ContextTypes

from bot.ai.transcribe import transcribe_audio
from bot.ai.llm import get_llm_response
from bot.utils.context import context_manager
from bot.utils.rate_limit import rate_limiter


async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Download voice message, transcribe with Whisper, then get LLM response."""
    if not update.message or not update.message.voice:
        return
    user_id = update.effective_user.id if update.effective_user else 0

    if not rate_limiter.is_allowed(user_id):
        await update.message.reply_text(
            "Слишком много запросов. Подожди немного."
        )
        return

    voice = update.message.voice
    file = await context.bot.get_file(voice.file_id)
    buf = io.BytesIO()
    await file.download_to_memory(buf)
    buf.seek(0)
    audio_bytes = buf.getvalue()

    try:
        text = await transcribe_audio(audio_bytes, "voice.ogg")
        context_manager.add_message(user_id, "user", text)
        response = await get_llm_response(user_id, context_manager)
        await update.message.reply_text(response)
    except Exception as e:
        await update.message.reply_text(f"Ошибка: {e!s}")
