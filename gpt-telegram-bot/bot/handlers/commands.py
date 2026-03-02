"""System commands: /start, /help, /reset."""
from telegram import Update
from telegram.ext import ContextTypes

from bot.utils.context import context_manager


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Welcome message on /start."""
    if not update.message:
        return
    await update.message.reply_text(
        "Привет! Я GPT-бот. Присылай текст, фото или голосовое."
        " Команды: /help — справка, /reset — очистить историю диалога."
    )


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """List commands on /help."""
    if not update.message:
        return
    await update.message.reply_text(
        "/start — Приветствие\n"
        "/help — Эта справка\n"
        "/reset — Очистить историю и начать заново"
    )


async def cmd_reset(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Clear chat history for this user (/reset)."""
    if not update.effective_user or not update.message:
        return
    user_id = update.effective_user.id
    context_manager.clear(user_id)
    await update.message.reply_text("История очищена. Можно начать заново.")
