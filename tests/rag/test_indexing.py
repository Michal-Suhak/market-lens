from market_lens.rag.chunking import chunk_document
from market_lens.rag.indexing import index_document
from market_lens.rag.qdrant import COLLECTION_NAME

LONG_TEXT = " ".join(f"word{i}" for i in range(500))


def test_index_document_writes_one_point_per_chunk(
    qdrant_client, embedder, db_session, make_document
):
    doc = make_document(text=LONG_TEXT)
    db_session.add(doc)
    db_session.commit()
    expected = len(chunk_document(doc))
    assert expected > 1

    written = index_document(qdrant_client, embedder, doc)

    assert written == expected
    assert qdrant_client.count(COLLECTION_NAME).count == expected


def test_index_document_is_idempotent(qdrant_client, embedder, db_session, make_document):
    doc = make_document(text=LONG_TEXT)
    db_session.add(doc)
    db_session.commit()
    expected = len(chunk_document(doc))

    index_document(qdrant_client, embedder, doc)
    index_document(qdrant_client, embedder, doc)

    assert qdrant_client.count(COLLECTION_NAME).count == expected


def test_index_document_attaches_metadata(qdrant_client, embedder, db_session, make_document):
    doc = make_document(institution="FED", doc_type="FOMC", text=LONG_TEXT)
    db_session.add(doc)
    db_session.commit()

    index_document(qdrant_client, embedder, doc)

    points, _ = qdrant_client.scroll(COLLECTION_NAME, limit=1, with_payload=True)
    payload = points[0].payload
    assert payload["institution"] == "FED"
    assert payload["doc_type"] == "FOMC"
    assert payload["doc_id"] == doc.id
    assert "date" in payload
