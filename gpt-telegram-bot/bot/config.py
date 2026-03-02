"""Environment variables and bot configuration."""
import os
from pathlib import Path

from dotenv import load_dotenv

# Load .env from project root (parent of bot/)
_env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(_env_path)

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")

# Optional: Gemini model names
LLM_MODEL = os.getenv("LLM_MODEL", "gemini-1.5-flash")
VISION_MODEL = os.getenv("VISION_MODEL", "gemini-1.5-flash")
MAX_CONTEXT_MESSAGES = int(os.getenv("MAX_CONTEXT_MESSAGES", "20"))
