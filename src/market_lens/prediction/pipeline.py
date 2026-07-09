from __future__ import annotations

from qdrant_client import QdrantClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from market_lens.llm.base import LLMClient
from market_lens.prediction.generate import generate_prediction
from market_lens.prediction.prompt import build_prompt
from market_lens.rag.embedder import Embedder
from market_lens.rag.search import search
from market_lens.replay.documents import available_documents
from market_lens.storage import Document, Event, Prediction


def predict_all_events(
    session: Session,
    qdrant_client: QdrantClient,
    embedder: Embedder,
    llm: LLMClient,
    *,
    pair: str,
    top_k: int = 5,
) -> int:
    """Predict every event without a prediction for this model yet; return the number written."""
    predicted = set(
        session.scalars(select(Prediction.event_id).where(Prediction.model == llm.model))
    )
    count = 0
    for event in session.scalars(select(Event)).all():
        if event.id in predicted:
            continue
        predict_event(session, qdrant_client, embedder, llm, event, pair=pair, top_k=top_k)
        count += 1
    return count


def predict_event(
    session: Session,
    qdrant_client: QdrantClient,
    embedder: Embedder,
    llm: LLMClient,
    event: Event,
    *,
    pair: str,
    top_k: int = 5,
) -> Prediction:
    """Build the point-in-time context for an event, ask the LLM, and persist a prediction."""
    statement = _event_statement(session, event)
    context = _pit_context(session, qdrant_client, embedder, event, statement, top_k)
    output = generate_prediction(llm, build_prompt(statement, context, pair=pair))
    prediction = Prediction(
        event=event,
        tone=output.tone,
        direction=output.direction,
        confidence=output.confidence,
        score=output.score,
        model=llm.model,
        ts_utc=event.ts_utc,
    )
    session.add(prediction)
    session.commit()
    return prediction


def _event_statement(session: Session, event: Event) -> str:
    document = session.scalars(
        select(Document).where(
            Document.institution == event.institution,
            Document.published_ts_utc == event.ts_utc,
        )
    ).first()
    return document.text if document is not None else ""


def _pit_context(
    session: Session,
    qdrant_client: QdrantClient,
    embedder: Embedder,
    event: Event,
    query: str,
    top_k: int,
) -> list[str]:
    if not query:
        return []
    prior = available_documents(session, event.ts_utc, institution=event.institution)
    doc_ids = [document.id for document in prior]
    if not doc_ids:
        return []
    hits = search(
        qdrant_client,
        embedder,
        query,
        institution=event.institution,
        doc_ids=doc_ids,
        limit=top_k,
    )
    return [hit.text for hit in hits]
