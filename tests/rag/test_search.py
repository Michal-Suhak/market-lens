from datetime import datetime, timedelta, timezone

import pytest

from market_lens.rag.indexing import index_document
from market_lens.rag.search import search

UTC = timezone.utc


@pytest.fixture
def indexed_fed_and_ecb(qdrant_client, embedder, db_session, make_document):
    t0 = datetime(2026, 1, 28, 19, 0, tzinfo=UTC)
    fed = make_document(
        institution="FED",
        doc_type="FOMC",
        published_ts_utc=t0,
        text="The Federal Reserve raised interest rates to curb inflation.",
    )
    ecb = make_document(
        institution="ECB",
        doc_type="PRESS",
        published_ts_utc=t0 - timedelta(days=1),
        text="The European Central Bank held interest rates amid slowing growth.",
    )
    db_session.add_all([fed, ecb])
    db_session.commit()
    index_document(qdrant_client, embedder, fed)
    index_document(qdrant_client, embedder, ecb)
    return qdrant_client


def test_fed_query_never_returns_ecb_chunks(indexed_fed_and_ecb, embedder):
    results = search(
        indexed_fed_and_ecb,
        embedder,
        "central bank interest rate decision",
        institution="FED",
        limit=10,
    )

    assert results
    assert all(hit.institution == "FED" for hit in results)


def test_ecb_query_never_returns_fed_chunks(indexed_fed_and_ecb, embedder):
    results = search(
        indexed_fed_and_ecb,
        embedder,
        "central bank interest rate decision",
        institution="ECB",
        limit=10,
    )

    assert results
    assert all(hit.institution == "ECB" for hit in results)


def test_search_filters_by_doc_ids(qdrant_client, embedder, db_session, make_document):
    t0 = datetime(2026, 1, 28, 19, 0, tzinfo=UTC)
    recent = make_document(
        institution="FED", doc_type="FOMC", published_ts_utc=t0, text="Fed raised rates."
    )
    older = make_document(
        institution="FED",
        doc_type="FOMC",
        published_ts_utc=t0 - timedelta(days=1),
        text="Fed held rates.",
    )
    db_session.add_all([recent, older])
    db_session.commit()
    index_document(qdrant_client, embedder, recent)
    index_document(qdrant_client, embedder, older)

    results = search(
        qdrant_client, embedder, "rates", institution="FED", doc_ids=[older.id], limit=10
    )

    assert results
    assert all(hit.doc_id == older.id for hit in results)
