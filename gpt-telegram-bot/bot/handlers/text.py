"""Handle raw text queries from users."""
from telegram import Update
from telegram.ext import ContextTypes

from bot.ai.llm import get_llm_response
from bot.utils.context import context_manager
from bot.utils.rate_limit import rate_limiter


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Receive and parse raw text from the user, then get LLM response."""
    if not update.message or not update.message.text:
        return
    raw_text = update.message.text.strip()
    user_id = update.effective_user.id if update.effective_user else 0

    if not rate_limiter.is_allowed(user_id):
        await update.message.reply_text(
            "Слишком много запросов. Подожди немного перед следующим сообщением."
        )
        return

    context_manager.add_message(user_id, "user", raw_text)
    try:
        response = await get_llm_response(user_id, context_manager)
        await update.message.reply_text(response)
    except Exception as e:
        await update.message.reply_text(f"Ошибка: {e!s}")
