"""LLM response generation using Google Gemini (google-genai v2026)."""
from bot.ai.ai_service import get_gemini_response


def _build_prompt_from_history(messages: list[dict]) -> str:
    """Format chat history into a single prompt for the model."""
    if not messages:
        return ""
    parts = []
    for m in messages:
        role_label = "User" if m["role"] == "user" else "Assistant"
        parts.append(f"{role_label}: {m['content']}")
    return "\n\n".join(parts)


async def get_llm_response(user_id: int, context_manager) -> str:
    """
    Generate response from chat history using async Gemini API.
    Adds assistant reply to context.
    """
    messages = context_manager.get_messages(user_id)
    if not messages:
        return "Отправь сообщение или голосовое, чтобы начать."

    prompt = _build_prompt_from_history(messages)
    response = await get_gemini_response(prompt)
    if response and not response.startswith("❌") and not response.startswith("🕒"):
        context_manager.add_message(user_id, "assistant", response)
    return response
