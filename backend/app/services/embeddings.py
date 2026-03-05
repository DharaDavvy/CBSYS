"""
FAISS-based vector store with ONNX MiniLM embeddings.

Replaces ChromaDB — loads a persisted FAISS index on startup and
exposes a `search()` helper for retrieving relevant curriculum chunks.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path

import faiss
import numpy as np
from chromadb.utils.embedding_functions.onnx_mini_lm_l6_v2 import ONNXMiniLM_L6_V2

from app.config import FAISS_DIR

# ── Constants ────────────────────────────────────────────────────────
INDEX_FILE = "index.faiss"
META_FILE = "metadata.json"
EMBEDDING_DIM = 384  # all-MiniLM-L6-v2 output dimension


# ── Document dataclass (lightweight replacement for LangChain Document) ──
@dataclass
class Document:
    page_content: str = ""
    metadata: dict = field(default_factory=dict)


# ── Module-level singletons ─────────────────────────────────────────
_embed_fn: ONNXMiniLM_L6_V2 | None = None
_index: faiss.IndexFlatIP | None = None
_metadata: list[dict] = []


def get_embed_fn() -> ONNXMiniLM_L6_V2:
    """Return (and cache) the ONNX embedding function."""
    global _embed_fn
    if _embed_fn is None:
        _embed_fn = ONNXMiniLM_L6_V2(preferred_providers=["CPUExecutionProvider"])
    return _embed_fn


def embed_texts(texts: list[str]) -> np.ndarray:
    """Embed a list of texts and return an (N, 384) float32 array, L2-normalised."""
    ef = get_embed_fn()
    vectors = np.array(ef(texts), dtype=np.float32)
    faiss.normalize_L2(vectors)
    return vectors


# ── Persistence ──────────────────────────────────────────────────────

def save_index(index: faiss.IndexFlatIP, metadata: list[dict], directory: str) -> None:
    """Write the FAISS index + metadata to disk."""
    os.makedirs(directory, exist_ok=True)
    faiss.write_index(index, os.path.join(directory, INDEX_FILE))
    with open(os.path.join(directory, META_FILE), "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False)


def load_index(directory: str) -> tuple[faiss.IndexFlatIP, list[dict]]:
    """Read a persisted FAISS index + metadata from disk."""
    idx = faiss.read_index(os.path.join(directory, INDEX_FILE))
    with open(os.path.join(directory, META_FILE), "r", encoding="utf-8") as f:
        meta = json.load(f)
    return idx, meta


# ── Init / getters ───────────────────────────────────────────────────

def init_vectorstore() -> None:
    """Load the persisted FAISS index. Called once at startup."""
    global _index, _metadata

    idx_path = os.path.join(FAISS_DIR, INDEX_FILE)
    if not os.path.exists(idx_path):
        print(f"[Embeddings] No FAISS index found at {FAISS_DIR} — run ingest.py first")
        _index = faiss.IndexFlatIP(EMBEDDING_DIM)
        _metadata = []
        return

    _index, _metadata = load_index(FAISS_DIR)
    print(f"[Embeddings] FAISS loaded — {_index.ntotal} vectors from {FAISS_DIR}")


def search(query: str, k: int = 5) -> list[Document]:
    """Embed *query* and return the top-k most similar curriculum chunks."""
    if _index is None or _index.ntotal == 0:
        return []

    q_vec = embed_texts([query])
    actual_k = min(k, _index.ntotal)
    distances, indices = _index.search(q_vec, actual_k)

    results: list[Document] = []
    for dist, idx in zip(distances[0], indices[0]):
        if idx == -1:
            continue
        meta = _metadata[idx]
        results.append(Document(
            page_content=meta["text"],
            metadata={k_: v for k_, v in meta.items() if k_ != "text"},
        ))
    return results
