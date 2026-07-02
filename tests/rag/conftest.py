import pytest
from qdrant_client import QdrantClient


@pytest.fixture
def qdrant_client() -> QdrantClient:
    return QdrantClient(":memory:")
