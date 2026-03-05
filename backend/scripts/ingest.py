"""
One-off script: Embed the CCMAS PDF into a FAISS index.

Usage:
    cd backend
    python scripts/ingest.py

Prerequisites:
    - Place 'Computing-CCMAS 2023-FINAL.pdf' in backend/data/
    - pip install -r requirements.txt
"""

import sys
from pathlib import Path

# Ensure the backend package is importable when running as a script
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pypdf import PdfReader

from app.config import FAISS_DIR, DATA_DIR, CHUNK_SIZE, CHUNK_OVERLAP
from app.services.embeddings import embed_texts, save_index, EMBEDDING_DIM
from app.services.text_splitter import split_text

import faiss


def main():
    data_dir = Path(DATA_DIR)
    pdf_files = sorted(data_dir.glob("*.pdf"))

    if not pdf_files:
        print(f"ERROR: No PDF files found in {data_dir}")
        sys.exit(1)

    print(f"Found {len(pdf_files)} PDF(s): {[p.name for p in pdf_files]}")

    # ── 1. Load all PDFs ─────────────────────────────────────────────
    pages_text = []
    for pdf_path in pdf_files:
        print(f"Loading PDF: {pdf_path.name}")
        reader = PdfReader(str(pdf_path))
        for i, page in enumerate(reader.pages):
            text = page.extract_text() or ""
            if text.strip():
                pages_text.append({"text": text, "page": i, "source": pdf_path.name})
        print(f"  Loaded {len(reader.pages)} page(s).")

    # ── 2. Split into chunks ─────────────────────────────────────────
    # ── 2. Split into chunks ─────────────────────────────────────────
    chunks: list[dict] = []
    for page_info in pages_text:
        splits = split_text(page_info["text"], chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
        for s in splits:
            chunks.append({
                "text": s,
                "page": page_info["page"],
                "source": page_info["source"],
            })
    print(f"  Split into {len(chunks)} chunk(s)  (size={CHUNK_SIZE}, overlap={CHUNK_OVERLAP}).")

    # ── 3. Embed in batches and build FAISS index ────────────────────
    print("Embedding chunks with ONNX MiniLM-L6-v2 ...")
    BATCH_SIZE = 64
    index = faiss.IndexFlatIP(EMBEDDING_DIM)

    for start in range(0, len(chunks), BATCH_SIZE):
        batch = chunks[start : start + BATCH_SIZE]
        texts = [c["text"] for c in batch]
        vectors = embed_texts(texts)  # already L2-normalised
        index.add(vectors)
        print(f"  Embedded {min(start + BATCH_SIZE, len(chunks))}/{len(chunks)} chunks", flush=True)

    # ── 4. Persist to disk ───────────────────────────────────────────
    print(f"Saving FAISS index to: {FAISS_DIR}")
    save_index(index, chunks, FAISS_DIR)

    # ── 5. Quick sanity check ────────────────────────────────────────
    from app.services.embeddings import init_vectorstore, search

    init_vectorstore()
    test_query = "What are the prerequisites for Computer Science courses?"
    results = search(test_query, k=3)

    print(f"\n{'='*60}")
    print(f"Ingestion complete! {len(chunks)} chunks stored in FAISS.")
    print(f"{'='*60}")
    print(f"\nSanity check — top 3 results for: \"{test_query}\"\n")
    for i, doc in enumerate(results, 1):
        page = doc.metadata.get("page", "?")
        print(f"  [{i}] (page {page}) {doc.page_content[:120]}...")
    print()


if __name__ == "__main__":
    main()
