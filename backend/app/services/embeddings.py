"""
FAISS-based vector store — embeddings via HuggingFace Inference API.

Uses the HF Inference API to embed text with all-MiniLM-L6-v2.
No local compiled dependencies (no onnxruntime, no torch).
Requires HF_API_TOKEN in .env.
"""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass, field

import httpx
import numpy as np
import faiss

from app.config import FAISS_DIR, HF_API_TOKEN

# ── Constants ────────────────────────────────────────────────────────
INDEX_FILE = "index.faiss"
META_FILE = "metadata.json"
EMBEDDING_DIM = 384  # all-MiniLM-L6-v2 output dimension
HF_EMBED_URL = (
    "https://router.huggingface.co/hf-inference/models/"
    "sentence-transformers/all-MiniLM-L6-v2/pipeline/feature-extraction"
)


# ── Document dataclass (lightweight replacement for LangChain Document) ──
@dataclass
class Document:
    page_content: str = ""
    metadata: dict = field(default_factory=dict)


# ── Module-level singletons ─────────────────────────────────────────
_index: faiss.IndexFlatIP | None = None
_metadata: list[dict] = []


def embed_texts(texts: list[str]) -> np.ndarray:
    """Embed texts via HF Inference API.

    Returns an (N, 384) float32 array, L2-normalised for FAISS cosine search.
    Retries up to 5 times on network errors or model cold-start (HTTP 503).
    """
    headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}
    last_exc: Exception | None = None
    for attempt in range(5):
        try:
            response = httpx.post(
                HF_EMBED_URL,
                headers=headers,
                json={"inputs": texts},
                timeout=60.0,
            )
            if response.status_code == 503:
                time.sleep(20)
                continue
            response.raise_for_status()
            vectors = np.array(response.json(), dtype=np.float32)
            faiss.normalize_L2(vectors)
            return vectors
        except (httpx.ConnectError, httpx.ReadTimeout, httpx.RemoteProtocolError) as exc:
            last_exc = exc
            wait = 10 * (attempt + 1)
            print(f"  [embed] network error ({exc}), retrying in {wait}s...")
            time.sleep(wait)
    raise RuntimeError(f"embed_texts failed after 5 attempts: {last_exc}") from last_exc


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
