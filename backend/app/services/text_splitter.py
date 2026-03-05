"""
Simple recursive text splitter — pure Python, no heavy dependencies.

Mimics LangChain's RecursiveCharacterTextSplitter behaviour:
tries to split on paragraph breaks first, then sentences, then words,
then characters, keeping chunks under `chunk_size` with `chunk_overlap`.
"""

from __future__ import annotations

SEPARATORS = ["\n\n", "\n", ". ", " ", ""]


def split_text(
    text: str,
    chunk_size: int = 500,
    chunk_overlap: int = 50,
    separators: list[str] | None = None,
) -> list[str]:
    """Split *text* into overlapping chunks of at most *chunk_size* characters."""
    if separators is None:
        separators = list(SEPARATORS)

    if not text or not text.strip():
        return []

    # If the text already fits, return it as-is
    if len(text) <= chunk_size:
        return [text.strip()] if text.strip() else []

    # Pick the first separator that actually occurs in the text
    sep = ""
    for s in separators:
        if s == "" or s in text:
            sep = s
            break

    # Split on the chosen separator
    if sep:
        parts = text.split(sep)
    else:
        parts = list(text)

    # Merge parts back into chunks that respect chunk_size
    chunks: list[str] = []
    current = ""

    for part in parts:
        candidate = (current + sep + part) if current else part
        if len(candidate) <= chunk_size:
            current = candidate
        else:
            if current:
                chunks.append(current.strip())
            # If a single part exceeds chunk_size, recurse with finer separators
            if len(part) > chunk_size:
                remaining_seps = separators[separators.index(sep) + 1 :] if sep in separators else [""]
                sub_chunks = split_text(part, chunk_size, chunk_overlap, remaining_seps)
                chunks.extend(sub_chunks)
                current = ""
            else:
                current = part

    if current and current.strip():
        chunks.append(current.strip())

    # Apply overlap: prepend the tail of the previous chunk to the next
    if chunk_overlap > 0 and len(chunks) > 1:
        overlapped: list[str] = [chunks[0]]
        for i in range(1, len(chunks)):
            prev_tail = chunks[i - 1][-chunk_overlap:]
            merged = prev_tail + " " + chunks[i]
            overlapped.append(merged.strip())
        chunks = overlapped

    return [c for c in chunks if c]
