from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, StatementError

from market_lens.storage import Event


def test_event_round_trip(db_session, make_event):
    db_session.add(make_event())
    db_session.commit()
    db_session.expire_all()

    event = db_session.scalars(select(Event)).one()

    assert event.institution == "FED"
    assert event.event_type == "FOMC"
    assert event.currency == "USD"
    assert event.ts_utc == datetime(2026, 1, 28, 19, 0, tzinfo=timezone.utc)
    assert event.forecast == 5.5
    assert event.actual == 5.5
    assert event.surprise is None


def test_ts_utc_normalized_to_utc(db_session, make_event):
    tokyo = timezone(timedelta(hours=9))

    db_session.add(make_event(ts_utc=datetime(2026, 1, 29, 4, 0, tzinfo=tokyo)))
    db_session.commit()
    db_session.expire_all()

    event = db_session.scalars(select(Event)).one()

    assert event.ts_utc == datetime(2026, 1, 28, 19, 0, tzinfo=timezone.utc)


def test_naive_ts_utc_rejected(db_session, make_event):
    db_session.add(make_event(ts_utc=datetime(2026, 1, 28, 19, 0)))

    with pytest.raises(StatementError):
        db_session.commit()


def test_duplicate_event_rejected(db_session, make_event):
    db_session.add(make_event())
    db_session.commit()

    db_session.add(make_event())

    with pytest.raises(IntegrityError):
        db_session.commit()
