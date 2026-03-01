"""System commands: /start, /help, /reset."""
from telegram import Update
from telegram.ext import ContextTypes

from bot.utils.context import context_manager


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Welcome message on /start."""
    if not update.message:
        return
    await update.message.reply_text(
        "Hi! I'm a GPT bot. Send me text, a photo, or a voice message. "
        "Use /help for commands, /reset to clear our conversation."
    )


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """List commands on /help."""
    if not update.message:
        return
    await update.message.reply_text(
        "/start — Welcome\n"
        "/help — This message\n"
        "/reset — Clear chat history and start over"
    )


async def cmd_reset(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Clear chat history for this user (/reset)."""
    if not update.effective_user or not update.message:
        return
    user_id = update.effective_user.id
    context_manager.clear(user_id)
    await update.message.reply_text("Context cleared. We can start over.")
