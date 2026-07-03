from __future__ import annotations

from dataclasses import dataclass

from qdrant_client import QdrantClient
from qdrant_client.models import FieldCondition, Filter, MatchValue

from market_lens.rag.embedder import Embedder
from market_lens.rag.qdrant import COLLECTION_NAME


@dataclass(frozen=True)
class Retrieved:
    text: str
    doc_id: int
    institution: str
    doc_type: str
    score: float


def search(
    client: QdrantClient,
    embedder: Embedder,
    query: str,
    *,
    institution: str,
    collection_name: str = COLLECTION_NAME,
    limit: int = 5,
) -> list[Retrieved]:
    """Vector search restricted to one institution; the filter is applied before the search."""
    query_vector = embedder.embed([query])[0]
    response = client.query_points(
        collection_name=collection_name,
        query=query_vector,
        query_filter=Filter(
            must=[FieldCondition(key="institution", match=MatchValue(value=institution))]
        ),
        limit=limit,
        with_payload=True,
    )
    return [
        Retrieved(
            text=point.payload["text"],
            doc_id=point.payload["doc_id"],
            institution=point.payload["institution"],
            doc_type=point.payload["doc_type"],
            score=point.score,
        )
        for point in response.points
    ]
