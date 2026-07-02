from datetime import date, datetime, timezone

from sqlalchemy import select

from market_lens.collectors.documents import (
    extract_statement_text,
    fetch_fed_statement,
    load_fed_statements,
)
from market_lens.storage import Document

UTC = timezone.utc


class _FakeResponse:
    def __init__(self, text):
        self.text = text

    def raise_for_status(self):
        pass


def test_extract_statement_text(fomc_statement_html):
    text = extract_statement_text(fomc_statement_html)

    assert "maintain the target range" in text
    assert "\n\n" in text


def test_fetch_fed_statement(monkeypatch, fomc_statement_html):
    monkeypatch.setattr(
        "market_lens.collectors.documents.requests.get",
        lambda url, headers=None, timeout=None: _FakeResponse(fomc_statement_html),
    )

    doc = fetch_fed_statement(date(2026, 1, 28))

    assert doc.institution == "FED"
    assert doc.doc_type == "FOMC"
    assert doc.published_ts_utc == datetime(
        2026, 1, 28, 19, 0, tzinfo=UTC
    )  # 14:00 EST -> 19:00 UTC
    assert "maintain the target range" in doc.text


def test_load_fed_statements(db_session, monkeypatch, fomc_statement_html):
    monkeypatch.setattr(
        "market_lens.collectors.documents.requests.get",
        lambda url, headers=None, timeout=None: _FakeResponse(fomc_statement_html),
    )

    count = load_fed_statements(db_session, [date(2026, 1, 28), date(2026, 6, 17)])

    stored = db_session.scalars(select(Document).order_by(Document.published_ts_utc)).all()
    assert count == 2
    assert len(stored) == 2
    assert stored[0].published_ts_utc == datetime(2026, 1, 28, 19, 0, tzinfo=UTC)  # EST
    assert stored[1].published_ts_utc == datetime(2026, 6, 17, 18, 0, tzinfo=UTC)  # EDT
