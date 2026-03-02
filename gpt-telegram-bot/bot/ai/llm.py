"""LLM response generation using Google Gemini."""
import asyncio
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


def _get_llm_response_sync(user_id: int, context_manager) -> str:
    """Sync call to Gemini. Run in thread from async handler."""
    messages = context_manager.get_messages(user_id)
    if not messages:
        return "Send a message or voice note to start."
    model = genai.GenerativeModel(LLM_MODEL)
    # Last message is the new user message; history is everything before it.
    generation_config = {"max_output_tokens": 1024}
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
    context_manager.add_message(user_id, "assistant", text)
    return text


async def get_llm_response(user_id: int, context_manager) -> str:
    """Generate response from chat history. Adds assistant reply to context."""
    return await asyncio.to_thread(_get_llm_response_sync, user_id, context_manager)
