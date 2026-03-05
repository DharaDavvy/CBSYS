"""
LLM client — wraps Ollama (local) with a Groq cloud fallback.

Exposes a single `generate()` coroutine used by the RAG service.
"""

import httpx
from langchain_community.llms import Ollama
from langchain_core.language_models import BaseLanguageModel

from app.config import (
    OLLAMA_BASE_URL,
    OLLAMA_MODEL,
    GROQ_API_KEY,
    GOOGLE_API_KEY,
    HF_API_TOKEN,
    LLM_TEMPERATURE,
)

# ── Module-level singletons (initialised lazily) ────────────────────
_llm: BaseLanguageModel | None = None


def _build_ollama() -> Ollama:
    """Return an Ollama LLM instance."""
    return Ollama(
        base_url=OLLAMA_BASE_URL,
        model=OLLAMA_MODEL,
        temperature=LLM_TEMPERATURE,
    )


def _build_groq():
    """Return a Groq-hosted Llama 3 instance (cloud fallback)."""
    from langchain_groq import ChatGroq
    return ChatGroq(
        model_name="llama3-70b-8192",
        groq_api_key=GROQ_API_KEY,
        temperature=LLM_TEMPERATURE,
    )


def _build_gemini():
    """Return a Google Gemini instance (cloud fallback)."""
    from langchain_google_genai import ChatGoogleGenerativeAI
    return ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        google_api_key=GOOGLE_API_KEY,
        temperature=LLM_TEMPERATURE,
    )


def _build_huggingface():
    """Return a HuggingFace Inference API wrapper.

    Uses huggingface_hub InferenceClient directly — more reliable than
    the LangChain wrapper for serverless inference models.
    Returns a thin adapter that exposes ainvoke().
    """
    return _HuggingFaceAdapter(
        model="meta-llama/Meta-Llama-3-8B-Instruct",
        token=HF_API_TOKEN,
        temperature=max(LLM_TEMPERATURE, 0.01),
        max_tokens=1024,
    )


class _HuggingFaceAdapter:
    """Minimal async adapter around huggingface_hub InferenceClient."""

    def __init__(self, model: str, token: str, temperature: float, max_tokens: int):
        from huggingface_hub import InferenceClient
        self.client = InferenceClient(token=token)
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

    async def ainvoke(self, prompt: str, **kwargs) -> str:
        """Send prompt to HF Inference API and return the text."""
        import asyncio
        return await asyncio.to_thread(self._call_sync, prompt)

    def _call_sync(self, prompt: str) -> str:
        response = self.client.chat_completion(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )
        return response.choices[0].message.content


async def _ollama_is_reachable() -> bool:
    """Quick health-check against the local Ollama server."""
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            resp = await client.get(f"{OLLAMA_BASE_URL}/api/tags")
            return resp.status_code == 200
    except (httpx.ConnectError, httpx.TimeoutException):
        return False


def get_llm() -> BaseLanguageModel:
    """Return the cached LLM instance (Ollama or Groq)."""
    global _llm
    if _llm is not None:
        return _llm
    # Default to Ollama; caller can swap via init_llm()
    _llm = _build_ollama()
    return _llm


async def init_llm() -> BaseLanguageModel:
    """Initialise the LLM at startup — picks Ollama if reachable, else Groq.

    Called once from the FastAPI lifespan handler.
    """
    global _llm
    if await _ollama_is_reachable():
        _llm = _build_ollama()
        print("[LLM] Using local Ollama →", OLLAMA_MODEL)
    elif HF_API_TOKEN:
        _llm = _build_huggingface()
        print("[LLM] Ollama unreachable \u2014 falling back to HuggingFace Inference")
    elif GOOGLE_API_KEY:
        _llm = _build_gemini()
        print("[LLM] Ollama unreachable \u2014 falling back to Google Gemini")
    elif GROQ_API_KEY:
        _llm = _build_groq()
        print("[LLM] Ollama unreachable \u2014 falling back to Groq cloud")
    else:
        _llm = _build_ollama()
        print("[LLM] WARNING: Ollama unreachable and no cloud API key set")
    return _llm


async def generate(prompt: str) -> str:
    """Send a prompt to the active LLM and return the text response."""
    llm = get_llm()
    # Both Ollama and ChatGroq support ainvoke via LangChain's interface
    result = await llm.ainvoke(prompt)
    # ChatGroq returns an AIMessage; Ollama returns a plain string
    if hasattr(result, "content"):
        return result.content
    return str(result)
