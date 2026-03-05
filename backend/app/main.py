"""
FastAPI application entry point.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import CORS_ORIGINS


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: load FAISS index + LLM + Firebase; Shutdown: cleanup."""
    # Load the FAISS vector store (ONNX embedding model + persisted index)
    from app.services.embeddings import init_vectorstore

    init_vectorstore()

    # Pick the best available LLM (Ollama local → Groq cloud)
    from app.services.llm import init_llm

    await init_llm()

    # Initialise Firebase Admin SDK + Firestore
    from app.models.firebase import init_firebase

    init_firebase()

    yield
    # Cleanup runs on shutdown (nothing to do yet)


app = FastAPI(
    title="CBSys — Career-Based Information System",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    return {"status": "ok"}


# ── Routers ──────────────────────────────────────────────────────────
from app.routers import chat, roadmap, users  # noqa: E402

app.include_router(chat.router)
app.include_router(roadmap.router)
app.include_router(users.router)
