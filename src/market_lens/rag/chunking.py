from __future__ import annotations

from dataclasses import dataclass

from market_lens.storage import Document

# Tune chunk size/overlap (in words) if retrieval quality is not good enough.
CHUNK_SIZE_WORDS = 200
CHUNK_OVERLAP_WORDS = 40


@dataclass(frozen=True)
class Chunk:
    doc_id: int
    index: int
    text: str


def chunk_text(
    text: str, *, size: int = CHUNK_SIZE_WORDS, overlap: int = CHUNK_OVERLAP_WORDS
) -> list[str]:
    if overlap >= size:
        raise ValueError("overlap must be smaller than size")
    words = text.split()
    if not words:
        return []
    step = size - overlap
    chunks = []
    start = 0
    while start < len(words):
        chunks.append(" ".join(words[start : start + size]))
        if start + size >= len(words):
            break
        start += step
    return chunks


def chunk_document(
    document: Document, *, size: int = CHUNK_SIZE_WORDS, overlap: int = CHUNK_OVERLAP_WORDS
) -> list[Chunk]:
    return [
        Chunk(doc_id=document.id, index=index, text=text)
        for index, text in enumerate(chunk_text(document.text, size=size, overlap=overlap))
    ]
