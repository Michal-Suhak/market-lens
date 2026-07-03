from __future__ import annotations

import uuid

from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct

from market_lens.rag.chunking import chunk_document
from market_lens.rag.embedder import Embedder
from market_lens.rag.qdrant import COLLECTION_NAME, ensure_collection
from market_lens.storage import Document

POINT_NAMESPACE = uuid.UUID("7c2e5f4a-3b1d-4e6a-9f8c-1a2b3c4d5e6f")


def _point_id(doc_id: int, index: int) -> str:
    return str(uuid.uuid5(POINT_NAMESPACE, f"{doc_id}:{index}"))


def index_document(
    client: QdrantClient,
    embedder: Embedder,
    document: Document,
    *,
    collection_name: str = COLLECTION_NAME,
) -> int:
    """Chunk, embed and upsert a document with metadata; returns the number of points written."""
    chunks = chunk_document(document)
    if not chunks:
        return 0
    ensure_collection(client, collection_name)
    vectors = embedder.embed([chunk.text for chunk in chunks])
    points = [
        PointStruct(
            id=_point_id(chunk.doc_id, chunk.index),
            vector=vector,
            payload={
                "doc_id": chunk.doc_id,
                "chunk_index": chunk.index,
                "text": chunk.text,
                "institution": document.institution,
                "doc_type": document.doc_type,
                "date": document.published_ts_utc.date().isoformat(),
            },
        )
        for chunk, vector in zip(chunks, vectors, strict=True)
    ]
    client.upsert(collection_name=collection_name, points=points)
    return len(points)
