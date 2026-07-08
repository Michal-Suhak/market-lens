from datetime import datetime, timedelta, timezone

from sqlalchemy import select

from market_lens.llm.base import LLMClient
from market_lens.prediction.pipeline import predict_event
from market_lens.rag.indexing import index_all_documents
from market_lens.storage import Prediction

UTC = timezone.utc
VALID = '{"tone": "hawkish", "direction": "down", "confidence": 0.8, "score": -0.6}'


class _RecordingStub(LLMClient):
    def __init__(self, response: str, model: str = "stub-model"):
        self._response = response
        self._model = model
        self.prompts: list[str] = []

    @property
    def model(self) -> str:
        return self._model

    def complete(self, prompt: str) -> str:
        self.prompts.append(prompt)
        return self._response


def test_predict_event_saves_prediction_at_t0(
    qdrant_client, embedder, db_session, make_event, make_document
):
    t0 = datetime(2026, 1, 28, 19, 0, tzinfo=UTC)
    event = make_event(ts_utc=t0)
    current = make_document(
        institution="FED",
        doc_type="FOMC",
        published_ts_utc=t0,
        text="Current statement: the Committee held rates.",
    )
    prior = make_document(
        institution="FED",
        doc_type="FOMC",
        published_ts_utc=t0 - timedelta(days=42),
        text="Prior guidance: inflation remains elevated.",
    )
    future = make_document(
        institution="FED",
        doc_type="FOMC",
        published_ts_utc=t0 + timedelta(days=42),
        text="Future leak: the Committee will cut.",
    )
    db_session.add_all([event, current, prior, future])
    db_session.commit()
    index_all_documents(qdrant_client, embedder, db_session)

    stub = _RecordingStub(VALID)
    predict_event(db_session, qdrant_client, embedder, stub, event, pair="EUR/USD")

    stored = db_session.scalars(select(Prediction)).one()
    assert stored.event_id == event.id
    assert stored.ts_utc == t0
    assert stored.tone == "hawkish"
    assert stored.direction == "down"
    assert stored.confidence == 0.8
    assert stored.score == -0.6
    assert stored.model == "stub-model"

    prompt = stub.prompts[0]
    assert "Prior guidance" in prompt
    assert "Future leak" not in prompt
