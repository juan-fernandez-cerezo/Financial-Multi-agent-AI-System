"""Central configuration — all env vars resolved here."""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ── LLM ───────────────────────────────────────────────────────────────────────
GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
GEMINI_MODEL_NAME: str = os.getenv("GEMINI_MODEL_NAME", "gemini-2.0-flash")

# ── Search ────────────────────────────────────────────────────────────────────
TAVILY_API_KEY: str = os.getenv("TAVILY_API_KEY", "")
USE_TAVILY: bool = bool(TAVILY_API_KEY)

# ── Output ────────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / os.getenv("OUTPUT_DIR", "outputs")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ── Shared LLM instance (crewai 1.x uses LiteLLM under the hood) ─────────────
from crewai import LLM

GEMINI_LLM = LLM(
    model=f"gemini/{GEMINI_MODEL_NAME}",
    api_key=GOOGLE_API_KEY,
    temperature=0.1,
)
