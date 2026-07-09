from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from qdrant_client import QdrantClient
from qdrant_client.models import FieldCondition, Filter, MatchAny, MatchValue

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
    doc_ids: Iterable[int] | None = None,
    collection_name: str = COLLECTION_NAME,
    limit: int = 5,
) -> list[Retrieved]:
    """Vector search restricted to one institution (and optional doc ids); filter runs first."""
    conditions = [FieldCondition(key="institution", match=MatchValue(value=institution))]
    if doc_ids is not None:
        conditions.append(FieldCondition(key="doc_id", match=MatchAny(any=list(doc_ids))))
    query_vector = embedder.embed([query])[0]
    response = client.query_points(
        collection_name=collection_name,
        query=query_vector,
        query_filter=Filter(must=conditions),
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
