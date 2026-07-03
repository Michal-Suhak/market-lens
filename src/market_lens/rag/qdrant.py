from __future__ import annotations

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

from market_lens.config import load_config

COLLECTION_NAME = "documents"
EMBEDDING_DIM = 384  # bge-small-en-v1.5 / all-MiniLM-L6-v2
DISTANCE = Distance.COSINE


def get_client() -> QdrantClient:
    return QdrantClient(url=load_config().secrets.qdrant_url)


def ensure_collection(client: QdrantClient, collection_name: str = COLLECTION_NAME) -> None:
    """Create the collection (vector size + cosine distance) if it does not exist yet."""
    if not client.collection_exists(collection_name):
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=EMBEDDING_DIM, distance=DISTANCE),
        )
