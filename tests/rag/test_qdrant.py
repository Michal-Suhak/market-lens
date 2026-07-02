from market_lens.rag.qdrant import COLLECTION_NAME, ensure_collection


def test_ensure_collection_creates_empty_collection(qdrant_client):
    ensure_collection(qdrant_client)

    assert qdrant_client.collection_exists(COLLECTION_NAME)
    assert qdrant_client.count(COLLECTION_NAME).count == 0


def test_ensure_collection_is_idempotent(qdrant_client):
    ensure_collection(qdrant_client)
    ensure_collection(qdrant_client)

    assert qdrant_client.collection_exists(COLLECTION_NAME)
