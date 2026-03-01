"""Environment variables and bot configuration."""
import os
from pathlib import Path

from dotenv import load_dotenv

# Load .env from project root (parent of bot/)
_env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(_env_path)

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Optional: model names
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o")
VISION_MODEL = os.getenv("VISION_MODEL", "gpt-4o")
MAX_CONTEXT_MESSAGES = int(os.getenv("MAX_CONTEXT_MESSAGES", "20"))
