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
LLM_MODEL = os.getenv("LLM_MODEL", "ggemini-2.0-flash")
VISION_MODEL = os.getenv("VISION_MODEL", "gemini-2.0-flash")
MAX_CONTEXT_MESSAGES = int(os.getenv("MAX_CONTEXT_MESSAGES", "20"))

# Rate limits (protect free-tier quotas; tune via .env)
RATE_LIMIT_WINDOW_SECONDS = float(os.getenv("RATE_LIMIT_WINDOW_SECONDS", "60"))
RATE_LIMIT_USER_MAX_REQUESTS = int(os.getenv("RATE_LIMIT_USER_MAX_REQUESTS", "2"))
RATE_LIMIT_GLOBAL_MAX_REQUESTS = int(os.getenv("RATE_LIMIT_GLOBAL_MAX_REQUESTS", "2"))
