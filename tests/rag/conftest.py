import pytest
from qdrant_client import QdrantClient

from market_lens.rag.embedder import Embedder


@pytest.fixture
def qdrant_client() -> QdrantClient:
    return QdrantClient(":memory:")


@pytest.fixture(scope="session")
def embedder() -> Embedder:
    return Embedder()
