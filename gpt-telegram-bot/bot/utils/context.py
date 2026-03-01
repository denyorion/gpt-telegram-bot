"""Chat history management for conversational context."""
from collections import defaultdict
from dataclasses import dataclass

from bot.config import MAX_CONTEXT_MESSAGES


@dataclass
class ChatMessage:
    role: str  # "user" | "assistant" | "system"
    content: str


class ContextManager:
    """In-memory chat history per user. Keeps last N messages to limit tokens."""

    def __init__(self, max_messages: int = MAX_CONTEXT_MESSAGES):
        self._history: dict[int, list[ChatMessage]] = defaultdict(list)
        self._max_messages = max_messages

    def add_message(self, user_id: int, role: str, content: str) -> None:
        self._history[user_id].append(ChatMessage(role=role, content=content))
        if len(self._history[user_id]) > self._max_messages:
            self._history[user_id] = self._history[user_id][-self._max_messages :]

    def get_messages(self, user_id: int) -> list[dict]:
        return [
            {"role": m.role, "content": m.content}
            for m in self._history[user_id]
        ]

    def clear(self, user_id: int) -> None:
        self._history[user_id].clear()


# Single instance for the whole bot
context_manager = ContextManager()
