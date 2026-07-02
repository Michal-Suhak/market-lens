from datetime import datetime, timedelta, timezone

from market_lens.replay.documents import available_documents

UTC = timezone.utc


def test_available_documents_excludes_at_or_after_as_of(db_session, make_document):
    t0 = datetime(2026, 1, 28, 19, 0, tzinfo=UTC)
    db_session.add_all(
        [
            make_document(published_ts_utc=t0 - timedelta(days=42), text="prior statement"),
            make_document(published_ts_utc=t0, text="the event statement"),
            make_document(published_ts_utc=t0 + timedelta(days=42), text="future statement"),
        ]
    )
    db_session.commit()

    docs = available_documents(db_session, t0)

    assert [doc.text for doc in docs] == ["prior statement"]


def test_available_documents_filters_by_institution(db_session, make_document):
    t0 = datetime(2026, 1, 28, 19, 0, tzinfo=UTC)
    db_session.add_all(
        [
            make_document(institution="FED", published_ts_utc=t0 - timedelta(days=1)),
            make_document(institution="ECB", published_ts_utc=t0 - timedelta(days=2)),
        ]
    )
    db_session.commit()

    docs = available_documents(db_session, t0, institution="FED")

    assert [doc.institution for doc in docs] == ["FED"]
