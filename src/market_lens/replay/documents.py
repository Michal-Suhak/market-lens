from __future__ import annotations

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from market_lens.storage import Document


def available_documents(
    session: Session, as_of: datetime, *, institution: str | None = None
) -> list[Document]:
    """Documents knowable at a point in time — only those published strictly before as_of."""
    stmt = select(Document).where(Document.published_ts_utc < as_of)
    if institution is not None:
        stmt = stmt.where(Document.institution == institution)
    return list(session.scalars(stmt.order_by(Document.published_ts_utc)))
