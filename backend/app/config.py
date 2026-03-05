"""
Application configuration — loads environment variables from .env
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from the backend/ directory
ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=ENV_PATH)

# ── Paths ────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent          # backend/
CHROMA_DIR = str(BASE_DIR / "chroma_store")               # legacy, kept for reference
FAISS_DIR = str(BASE_DIR / "faiss_store")
DATA_DIR = str(BASE_DIR / "data")

# ── LLM Settings ────────────────────────────────────────────────────
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
HF_API_TOKEN = os.getenv("HF_API_TOKEN", "")
LLM_TEMPERATURE = 0  # Deterministic for curriculum queries

# ── Embedding ────────────────────────────────────────────────────────
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50

# ── Firebase ─────────────────────────────────────────────────────────
_raw_creds = os.getenv("FIREBASE_CREDENTIALS", "")
# Resolve relative paths against BASE_DIR so it works regardless of where uvicorn is launched
if _raw_creds and not os.path.isabs(_raw_creds):
    FIREBASE_CREDENTIALS = str(BASE_DIR / _raw_creds)
else:
    FIREBASE_CREDENTIALS = _raw_creds

# ── CORS ─────────────────────────────────────────────────────────────
CORS_ORIGINS = [
    "http://localhost:5173",   # Vite dev server
    "http://127.0.0.1:5173",
]
