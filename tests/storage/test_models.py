from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, StatementError

from market_lens.storage import Document, Event, Outcome, Prediction, Price


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


def test_document_round_trip(db_session, make_document):
    db_session.add(make_document())
    db_session.commit()
    db_session.expire_all()

    doc = db_session.scalars(select(Document)).one()

    assert doc.institution == "FED"
    assert doc.doc_type == "FOMC"
    assert doc.published_ts_utc == datetime(2026, 1, 28, 19, 0, tzinfo=timezone.utc)
    assert doc.text.startswith("The Committee")


def test_price_round_trip(db_session, make_price):
    db_session.add(make_price())
    db_session.commit()
    db_session.expire_all()

    price = db_session.scalars(select(Price)).one()

    assert price.pair == "EUR/USD"
    assert price.ts_utc == datetime(2026, 1, 28, 19, 0, tzinfo=timezone.utc)
    assert price.open == 1.0850
    assert price.high == 1.0860
    assert price.low == 1.0845
    assert price.close == 1.0858


def test_duplicate_price_bar_rejected(db_session, make_price):
    db_session.add(make_price())
    db_session.commit()

    db_session.add(make_price())

    with pytest.raises(IntegrityError):
        db_session.commit()


def test_prediction_round_trip(db_session, make_prediction):
    db_session.add(make_prediction())
    db_session.commit()
    db_session.expire_all()

    prediction = db_session.scalars(select(Prediction)).one()

    assert prediction.tone == "hawkish"
    assert prediction.direction == "down_eurusd"
    assert prediction.confidence == 0.84
    assert prediction.score == 0.62
    assert prediction.model == "gemini-2.5-flash"
    assert prediction.event.institution == "FED"


def test_duplicate_prediction_rejected(db_session, make_event, make_prediction):
    event = make_event()
    db_session.add(make_prediction(event=event))
    db_session.commit()

    db_session.add(make_prediction(event=event))

    with pytest.raises(IntegrityError):
        db_session.commit()


def test_outcome_round_trip(db_session, make_outcome):
    db_session.add(make_outcome(ret_24h=None, realized_direction=None))
    db_session.commit()
    db_session.expire_all()

    outcome = db_session.scalars(select(Outcome)).one()

    assert outcome.pair == "EUR/USD"
    assert outcome.ret_1h == 0.0012
    assert outcome.ret_4h == 0.0020
    assert outcome.ret_24h is None
    assert outcome.realized_direction is None
    assert outcome.event.institution == "FED"
