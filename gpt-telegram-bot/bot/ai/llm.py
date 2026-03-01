"""LLM response generation using OpenAI GPT."""
from openai import AsyncOpenAI

from bot.config import LLM_MODEL, OPENAI_API_KEY

client = AsyncOpenAI(api_key=OPENAI_API_KEY)


async def get_llm_response(user_id: int, context_manager) -> str:
    """Generate response from chat history. Adds assistant reply to context."""
    messages = context_manager.get_messages(user_id)
    if not messages:
        return "Send a message or voice note to start."
    response = await client.chat.completions.create(
        model=LLM_MODEL,
        messages=messages,
        max_tokens=1024,
    )
    text = response.choices[0].message.content or ""
    context_manager.add_message(user_id, "assistant", text)
    return text
