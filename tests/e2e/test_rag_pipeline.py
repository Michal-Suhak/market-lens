from datetime import datetime, timedelta, timezone

import pytest

from market_lens.rag.indexing import index_all_documents
from market_lens.rag.search import search

UTC = timezone.utc


@pytest.fixture
def indexed_corpus(qdrant_client, embedder, db_session, make_document):
    t0 = datetime(2026, 1, 28, 19, 0, tzinfo=UTC)
    db_session.add_all(
        [
            make_document(
                institution="FED",
                doc_type="FOMC",
                published_ts_utc=t0,
                text="The Federal Reserve raised interest rates to curb persistent inflation.",
            ),
            make_document(
                institution="ECB",
                doc_type="PRESS",
                published_ts_utc=t0 - timedelta(days=1),
                text="The European Central Bank held rates steady amid slowing euro-area growth.",
            ),
        ]
    )
    db_session.commit()
    index_all_documents(qdrant_client, embedder, db_session)
    return qdrant_client


def test_rag_build_then_search_isolates_by_institution(indexed_corpus, embedder):
    fed_hits = search(
        indexed_corpus, embedder, "interest rate decision", institution="FED", limit=10
    )
    ecb_hits = search(
        indexed_corpus, embedder, "interest rate decision", institution="ECB", limit=10
    )

    assert fed_hits and all(hit.institution == "FED" for hit in fed_hits)
    assert ecb_hits and all(hit.institution == "ECB" for hit in ecb_hits)
    assert not any("European Central Bank" in hit.text for hit in fed_hits)
