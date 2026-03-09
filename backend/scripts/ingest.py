"""
One-off script: Embed the CCMAS PDF into a FAISS index.

Usage:
    cd backend
    python scripts/ingest.py

Prerequisites:
    - Place 'Computing-CCMAS 2023-FINAL.pdf' in backend/data/
    - pip install -r requirements.txt
"""

import os
import sys
from pathlib import Path

# Ensure the backend package is importable when running as a script
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pypdf import PdfReader

from app.config import FAISS_DIR, DATA_DIR, CHUNK_SIZE, CHUNK_OVERLAP
from app.services.embeddings import embed_texts, save_index, load_index, EMBEDDING_DIM
from app.services.text_splitter import split_text

import faiss
import re


# ── Metadata extraction ──────────────────────────────────────────────

def extract_chunk_metadata(text: str, page: int, source: str) -> dict:
    """Parse structured metadata from a curriculum chunk's text.

    Extracts: course_code, level, department, semester, units,
              prerequisites, related_codes, section.
    All fields are optional — only present when confidently detected.
    """
    meta: dict = {"page": page, "source": source}

    # Course codes — e.g. CSC 301, STA 111, MTH 211
    codes = re.findall(r'\b([A-Z]{2,4})\s*(\d{3})\b', text)
    if codes:
        dept_abbr, num = codes[0]
        meta["course_code"] = f"{dept_abbr} {num}"
        meta["level"] = int(num[0]) * 100        # 301 → 300
        meta["department"] = dept_abbr
        unique_codes = list(dict.fromkeys(f"{d} {n}" for d, n in codes))
        if len(unique_codes) > 1:
            meta["related_codes"] = unique_codes

    # Credit units — e.g. "3 Units", "2 Credit Hours"
    units_match = re.search(r'\b(\d+)\s*(?:credit\s*)?(?:units?|hours?)\b', text, re.IGNORECASE)
    if units_match:
        meta["units"] = int(units_match.group(1))

    # Semester
    sem_match = re.search(r'\b(first|second|1st|2nd)\s+semester\b', text, re.IGNORECASE)
    if sem_match:
        meta["semester"] = 1 if sem_match.group(1).lower() in ("first", "1st") else 2
    else:
        sem_num = re.search(r'\bsemester\s*([12])\b', text, re.IGNORECASE)
        if sem_num:
            meta["semester"] = int(sem_num.group(1))

    # Prerequisites
    prereq_match = re.search(
        r'pre[-\s]?requisites?\s*[:\-]?\s*([A-Z]{2,4}\s*\d{3}(?:\s*[,/]\s*[A-Z]{2,4}\s*\d{3})*)',
        text, re.IGNORECASE,
    )
    if prereq_match:
        raw = prereq_match.group(1)
        meta["prerequisites"] = [p.strip() for p in re.split(r'[,/]\s*', raw)]

    # Section number — e.g. "3.2", "Section 4.1.2"
    section_match = re.search(r'(?:^|\bsection\s+)(\d+\.\d+(?:\.\d+)?)\b', text, re.IGNORECASE | re.MULTILINE)
    if section_match:
        meta["section"] = section_match.group(1)

    return meta


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
            meta = extract_chunk_metadata(s, page_info["page"], page_info["source"])
            meta["text"] = s
            chunks.append(meta)
    print(f"  Split into {len(chunks)} chunk(s)  (size={CHUNK_SIZE}, overlap={CHUNK_OVERLAP}).")

    # ── 3. Embed in batches and build FAISS index ────────────────────
    checkpoint_index_path = os.path.join(FAISS_DIR, "index.faiss")
    checkpoint_meta_path = os.path.join(FAISS_DIR, "metadata.json")

    # Skip entirely if a complete index already exists
    if os.path.exists(checkpoint_index_path) and os.path.exists(checkpoint_meta_path):
        index, existing_meta = load_index(FAISS_DIR)
        if len(existing_meta) >= len(chunks):
            print(f"  Index already complete ({len(existing_meta)} chunks) — skipping embedding.")
            checkpoint_meta = existing_meta
            chunks_remaining = []
        else:
            index, checkpoint_meta = load_index(FAISS_DIR)
            start_chunk = len(checkpoint_meta)
            print(f"  Resuming from chunk {start_chunk}/{len(chunks)} (checkpoint found)")
            chunks_remaining = chunks[start_chunk:]
    else:
        index = faiss.IndexFlatIP(EMBEDDING_DIM)
        checkpoint_meta = []
        chunks_remaining = chunks

    print("Embedding chunks with HuggingFace API ...")
    BATCH_SIZE = 16
    start_chunk = len(checkpoint_meta)

    for batch_start in range(0, len(chunks_remaining), BATCH_SIZE):
        batch = chunks_remaining[batch_start : batch_start + BATCH_SIZE]
        texts = [c["text"] for c in batch]
        vectors = embed_texts(texts)  # already L2-normalised
        index.add(vectors)
        checkpoint_meta.extend(batch)
        done = start_chunk + batch_start + len(batch)
        print(f"  Embedded {done}/{len(chunks)} chunks", flush=True)
        # Save checkpoint after every batch so we can resume on failure
        save_index(index, checkpoint_meta, FAISS_DIR)

    # ── 4. Final save ────────────────────────────────────────────────
    print(f"Saving FAISS index to: {FAISS_DIR}")
    save_index(index, checkpoint_meta, FAISS_DIR)

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
