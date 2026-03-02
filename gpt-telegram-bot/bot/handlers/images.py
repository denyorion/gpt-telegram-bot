"""Handle photos for vision (e.g. GPT-4o Vision)."""
import io
import math
from telegram import Update
from telegram.ext import ContextTypes

from bot.ai.vision import analyze_image
from bot.utils.context import context_manager
from bot.utils.rate_limit import allow_request


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Accept photos for vision analysis."""
    if not update.message or not update.message.photo:
        return
    user_id = update.effective_user.id if update.effective_user else 0

    allowed, wait_s = allow_request(user_id, cost=1)
    if not allowed:
        wait_text = f"{max(1, math.ceil(wait_s))} сек."
        await update.message.reply_text(
            f"Слишком много запросов. Подожди {wait_text}."
        )
        return

    photo = update.message.photo[-1]
    caption = (update.message.caption or "").strip()

    file = await context.bot.get_file(photo.file_id)
    buf = io.BytesIO()
    await file.download_to_memory(buf)
    buf.seek(0)
    image_bytes = buf.read()

    try:
        result = await analyze_image(image_bytes, caption)
        context_manager.add_message(user_id, "user", caption or "[Image]")
        context_manager.add_message(user_id, "assistant", result)
        await update.message.reply_text(result)
    except Exception as e:
        await update.message.reply_text(f"Ошибка: {e!s}")
