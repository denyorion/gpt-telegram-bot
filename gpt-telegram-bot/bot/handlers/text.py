"""Handle raw text queries from users."""
import math
from telegram import Update
from telegram.ext import ContextTypes

from bot.ai.llm import get_llm_response
from bot.utils.context import context_manager
from bot.utils.rate_limit import allow_request


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Receive and parse raw text from the user, then get LLM response."""
    if not update.message or not update.message.text:
        return
    raw_text = update.message.text.strip()
    user_id = update.effective_user.id if update.effective_user else 0

    allowed, wait_s = allow_request(user_id, cost=1)
    if not allowed:
        wait_text = f"{max(1, math.ceil(wait_s))} сек."
        await update.message.reply_text(
            f"Слишком много запросов. Подожди {wait_text} перед следующим сообщением."
        )
        return

    context_manager.add_message(user_id, "user", raw_text)
    try:
        response = await get_llm_response(user_id, context_manager)
        await update.message.reply_text(response)
    except Exception as e:
        await update.message.reply_text(f"Ошибка: {e!s}")
