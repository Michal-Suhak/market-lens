from datetime import datetime, timezone

from sqlalchemy import select

from market_lens.llm.base import LLMClient
from market_lens.prediction.pipeline import predict_all_events
from market_lens.rag.indexing import index_all_documents
from market_lens.storage import Prediction

UTC = timezone.utc
VALID = '{"tone": "neutral", "direction": "flat", "confidence": 0.5, "score": 0.0}'


class _StubLLM(LLMClient):
    def __init__(self, response: str = VALID, model: str = "stub-model"):
        self._response = response
        self._model = model

    @property
    def model(self) -> str:
        return self._model

    def complete(self, prompt: str) -> str:
        return self._response


def test_predict_all_events_fills_the_table(
    qdrant_client, embedder, db_session, make_event, make_document
):
    t0 = datetime(2026, 1, 28, 19, 0, tzinfo=UTC)
    t1 = datetime(2026, 3, 18, 18, 0, tzinfo=UTC)
    db_session.add_all(
        [
            make_event(ts_utc=t0),
            make_event(ts_utc=t1),
            make_document(institution="FED", doc_type="FOMC", published_ts_utc=t0, text="one"),
            make_document(institution="FED", doc_type="FOMC", published_ts_utc=t1, text="two"),
        ]
    )
    db_session.commit()
    index_all_documents(qdrant_client, embedder, db_session)

    count = predict_all_events(db_session, qdrant_client, embedder, _StubLLM(), pair="EUR/USD")

    assert count == 2
    assert len(db_session.scalars(select(Prediction)).all()) == 2


def test_predict_all_events_is_idempotent(
    qdrant_client, embedder, db_session, make_event, make_document
):
    t0 = datetime(2026, 1, 28, 19, 0, tzinfo=UTC)
    db_session.add_all(
        [
            make_event(ts_utc=t0),
            make_document(institution="FED", doc_type="FOMC", published_ts_utc=t0, text="one"),
        ]
    )
    db_session.commit()

    predict_all_events(db_session, qdrant_client, embedder, _StubLLM(), pair="EUR/USD")
    predict_all_events(db_session, qdrant_client, embedder, _StubLLM(), pair="EUR/USD")

    assert len(db_session.scalars(select(Prediction)).all()) == 1
