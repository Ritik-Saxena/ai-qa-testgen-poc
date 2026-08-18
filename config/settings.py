import os
import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

MAX_TOKENS = int(os.getenv("MAX_TOKENS", 8000))
LLM_MODEL = os.getenv("LLM_MODEL")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not LLM_MODEL:
    raise RuntimeError("LLM_MODEL environment variable is not set. Please set it in the .env file.")
if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY environment variable is not set. Please set it in the .env file.")
if MAX_TOKENS <= 0:
    raise RuntimeError("MAX_TOKENS must be greater than 0.")