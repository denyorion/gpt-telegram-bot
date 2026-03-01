# Project Overview
GPT Telegram bot working with text, images, and voice (OpenAI API).

# Core Functionalities

1. Input Handling (Multimodal Processing)
Text Analysis: Receives and parses raw text queries from users.
Image Processing: Accepts images (photos, documents, screenshots) for analysis via vision models (e.g., GPT-4o Vision).
Voice-to-Text (Transcription): Receives voice messages, transcribes audio content into text using automatic speech recognition (e.g., OpenAI Whisper API).
Context Management: Maintains chat history to support conversational context and follow-up questions.
2. AI Processing Engine
Natural Language Understanding: Interprets user intent from text, transcribed audio, or image descriptions.
LLM Response Generation: Generates intelligent, context-aware text responses using GPT models.
Image Interpretation: Analyzes content within images to answer questions, describe scenes, or extract text (OCR).
Image Generation (Optional): Generates new images based on text prompts (e.g., integrating DALL-E 3).
3. Output Handling
Text Responses: Sends formatted text messages (Markdown/HTML support) as responses.
Image Delivery: Sends generated images or analyzed image results back to the chat.
Text-to-Speech (Optional): Converts text responses into audio files and sends them as voice messages.
4. System & Security
Command Handling: Processes system commands (e.g., /start, /help, /reset to clear context).
Rate Limiting: Protects against spam and manages API usage costs.
Error Handling: Provides user feedback on failed API requests or invalid file formats.

# Recommended Project Structure
bot/
├── handlers/         # Multimodal Processing
│   ├── text.py       # Raw text queries, Parsing
│   ├── images.py     # Vision models integration (GPT-4o Vision)
│   └── voice.py      # Voice-to-Text (Whisper API)
├── ai/               # Processing Engine
│   ├── llm.py        # Response generation
│   ├── vision.py     # OCR / Scene analysis
│   └── tts.py        # Text-to-Speech (Optional)
├── utils/            # System & Security
│   ├── context.py    # Chat history management
│   ├── db.py         # Database for history
│   └── rate_limit.py # API usage management
├── config.py         # Environment variables (.env)
└── main.py           # Bot entry point

# Notes
- Separate handlers by modality for maintainability.
- Keep AI logic isolated from Telegram bot logic.
- Use context management to maintain conversation flow.

# Documentation
## Input Handling (Multimodal Processing)

1. Text handler (bot/handlers/text.py)
```
# bot/handlers/text.py
from telegram import Update
from telegram.ext import ContextTypes

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Receive and parse raw text from the user."""
    if not update.message or not update.message.text:
        return
    raw_text = update.message.text.strip()
    user_id = update.effective_user.id if update.effective_user else 0
    
    # Pass to context + AI (your ai/llm.py would consume this)
    # await context_manager.add_message(user_id, "user", raw_text)
    # response = await get_llm_response(user_id)
    await update.message.reply_text(f"Received text: {raw_text[:100]}...")
    ```
  
   2. Image handler (bot/handlers/images.py)
   ```
    # bot/handlers/images.py
import io
from telegram import Update
from telegram.ext import ContextTypes

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Accept photos for vision (e.g. GPT-4o Vision)."""
    if not update.message or not update.message.photo:
        return
    # Take largest size
    photo = update.message.photo[-1]
    caption = (update.message.caption or "").strip()
    
    # Download file to bytes (needed for OpenAI Vision)
    file = await context.bot.get_file(photo.file_id)
    buf = io.BytesIO()
    await file.download_to_memory(buf)
    buf.seek(0)
    image_bytes = buf.read()
    
    # Call vision API (your ai/vision.py)
    # result = await analyze_image(image_bytes, caption)
    await update.message.reply_text(f"Image received ({len(image_bytes)} bytes). Caption: {caption or '(none)'}")
    ```

3. Voice handler (bot/handlers/voice.py)
```
# bot/handlers/voice.py
import io
from telegram import Update
from telegram.ext import ContextTypes

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Download voice message and transcribe with Whisper."""
    if not update.message or not update.message.voice:
        return
    
    voice = update.message.voice
    file = await context.bot.get_file(voice.file_id)
    
    buf = io.BytesIO()
    await file.download_to_memory(buf)
    buf.seek(0)
    # OpenAI Whisper expects a file-like object or file path
    # audio_file = ("voice.ogg", buf.getvalue())
    
    # Transcribe (your ai/ or external Whisper call)
    # text = await transcribe_audio(audio_file)
    # await context_manager.add_message(user_id, "user", text)
    # response = await get_llm_response(user_id)
    await update.message.reply_text("Voice received (transcription would go here).")
    ```
   
   4. Context management (used by all handlers)
    ```
    # bot/utils/context.py (simplified)
from collections import defaultdict
from dataclasses import dataclass

@dataclass
class ChatMessage:
    role: str  # "user" | "assistant" | "system"
    content: str

def get_context_manager():
    history: dict[int, list[ChatMessage]] = defaultdict(list)
    
    def add_message(user_id: int, role: str, content: str) -> None:
        history[user_id].append(ChatMessage(role=role, content=content))
        # Optional: keep last N messages to limit tokens
        if len(history[user_id]) > 20:
            history[user_id] = history[user_id][-20:]
    
    def get_messages(user_id: int) -> list[dict]:
        return [
            {"role": m.role, "content": m.content}
            for m in history[user_id]
        ]
    
    def clear(user_id: int) -> None:
        history[user_id].clear()
    
    return type("ContextManager", (), {"add_message": add_message, "get_messages": get_messages, "clear": clear})()
    ```
## AI Processing Engine
1. Image analysis (Vision) — bot/ai/vision.py
```
# bot/ai/vision.py
import base64
from openai import AsyncOpenAI

client = AsyncOpenAI()  # uses OPENAI_API_KEY from env

async def analyze_image(
    image_bytes: bytes,
    user_prompt: str = "",
    model: str = "gpt-4o"
) -> str:
    """
    Send image to GPT-4o Vision. user_prompt can be caption or question.
    """
    b64 = base64.standard_b64encode(image_bytes).decode("utf-8")
    # Determine media type (Telegram often sends JPEG)
    media_type = "image/jpeg"
    if image_bytes[:8].startswith(b"\x89PNG"):
        media_type = "image/png"
    elif image_bytes[:4] == b"RIFF" and image_bytes[8:12] == b"WEBP":
        media_type = "image/webp"

    content = [
        {
            "type": "image_url",
            "image_url": {"url": f"data:{media_type};base64,{b64}"}
        }
    ]
    if user_prompt:
        content.insert(0, {"type": "text", "text": user_prompt})

    response = await client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": content}],
        max_tokens=1024,
    )
    return response.choices[0].message.content or ""
```

Usage in bot/handlers/images.py:
```
# In handle_photo(), after getting image_bytes and caption:
from bot.ai.vision import analyze_image

result = await analyze_image(image_bytes, caption)
await context_manager.add_message(user_id, "user", caption or "[Image]")
await context_manager.add_message(user_id, "assistant", result)
await update.message.reply_text(result)
```

2. Voice transcription (Whisper) — bot/ai/transcribe.py
```
# bot/ai/transcribe.py
from openai import AsyncOpenAI

client = AsyncOpenAI()

async def transcribe_audio(audio_bytes: bytes, filename: str = "voice.ogg") -> str:
    """
    Transcribe voice message with Whisper. Telegram sends OGG/Opus.
    """
    from io import BytesIO
    audio_file = BytesIO(audio_bytes)
    audio_file.name = filename

    response = await client.audio.transcriptions.create(
        model="whisper-1",
        file=audio_file,
        response_format="text",
        language=None,  # auto-detect, or e.g. "ru" / "en"
    )
    return response if isinstance(response, str) else response.get("text", "")
```
Usage in bot/handlers/voice.py:
```
# In handle_voice(), after downloading to buf:
from bot.ai.transcribe import transcribe_audio

audio_bytes = buf.getvalue()
text = await transcribe_audio(audio_bytes, "voice.ogg")
context_manager.add_message(user_id, "user", text)
# Then get LLM response from history and reply
response = await get_llm_response(user_id)  # your bot/ai/llm.py
await update.message.reply_text(response)
```

3. /reset (clear context) — in bot/handlers/ or main.py
```
# bot/handlers/commands.py (or in main.py)
from telegram import Update
from telegram.ext import ContextTypes
# Assuming you have a single context manager instance
from bot.utils.context import context_manager

async def cmd_reset(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Clear chat history for this user (/reset)."""
    if not update.effective_user:
        return
    user_id = update.effective_user.id
    context_manager.clear(user_id)
    await update.message.reply_text("Context cleared. We can start over.")
    ```

    Register in main.py:
    ```
    from telegram.ext import Application, CommandHandler
from bot.handlers.commands import cmd_reset

app.add_handler(CommandHandler("reset", cmd_reset))
```

4. Minimal get_llm_response (for context + text/transcript)
```
# bot/ai/llm.py
from openai import AsyncOpenAI

client = AsyncOpenAI()

async def get_llm_response(user_id: int, context_manager) -> str:
    messages = context_manager.get_messages(user_id)
    if not messages:
        return "Send a message or voice note to start."
    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        max_tokens=1024,
    )
    text = response.choices[0].message.content or ""
    context_manager.add_message(user_id, "assistant", text)
    return text
```