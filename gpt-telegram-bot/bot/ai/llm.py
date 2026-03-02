"""LLM response generation using Google Gemini."""
import asyncio
import random
import time
import google.generativeai as genai

from bot.config import LLM_MODEL, GOOGLE_API_KEY

genai.configure(api_key=GOOGLE_API_KEY)


def _messages_to_history(messages: list[dict]) -> list[dict]:
    """Convert context_manager format (role/content) to Gemini history (role/parts)."""
    history = []
    for m in messages:
        role = "model" if m["role"] == "assistant" else m["role"]
        history.append({"role": role, "parts": [{"text": m["content"]}]})
    return history


def _is_rate_limit_error(exc: Exception) -> bool:
    msg = str(exc)
    name = exc.__class__.__name__.lower()
    return (
        "429" in msg
        or "resource_exhausted" in msg.lower()
        or "too many requests" in msg.lower()
        or "ratelimit" in name
        or "toomanyrequests" in name
        or "resourceexhausted" in name
    )


def _get_llm_response_sync(user_id: int, context_manager) -> str:
    """Sync call to Gemini. Run in thread from async handler."""
    messages = context_manager.get_messages(user_id)
    if not messages:
        return "Send a message or voice note to start."
    model = genai.GenerativeModel(LLM_MODEL)
    # Last message is the new user message; history is everything before it.
    generation_config = {"max_output_tokens": 1024}
    max_retries = 3
    for attempt in range(max_retries + 1):
        try:
            if len(messages) == 1:
                response = model.generate_content(
                    messages[0]["content"],
                    generation_config=generation_config,
                )
            else:
                history = _messages_to_history(messages[:-1])
                chat = model.start_chat(history=history)
                response = chat.send_message(
                    messages[-1]["content"],
                    generation_config=generation_config,
                )
            text = (response.text or "").strip()
            if text:
                context_manager.add_message(user_id, "assistant", text)
            return text or "Не смог сгенерировать ответ. Попробуй переформулировать."
        except Exception as e:
            if _is_rate_limit_error(e):
                if attempt < max_retries:
                    backoff = min(60.0, (2**attempt) + random.random())
                    time.sleep(backoff)
                    continue
                return (
                    "Сейчас слишком много запросов к Gemini (лимит). "
                    "Пожалуйста, подожди примерно минуту и попробуй снова."
                )
            raise


async def get_llm_response(user_id: int, context_manager) -> str:
    """Generate response from chat history. Adds assistant reply to context."""
    return await asyncio.to_thread(_get_llm_response_sync, user_id, context_manager)
