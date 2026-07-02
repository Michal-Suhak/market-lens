from datetime import datetime, timedelta, timezone

from market_lens.replay.documents import available_documents
from market_lens.replay.prices import available_prices

UTC = timezone.utc


def test_no_future_data_leaks_through_pit_accessors(db_session, make_price, make_document):
    t0 = datetime(2026, 1, 28, 19, 0, tzinfo=UTC)
    future = t0 + timedelta(hours=1)
    db_session.add_all(
        [
            make_price(ts_utc=t0, close=1.10),
            make_price(ts_utc=future, close=1.20),
            make_document(published_ts_utc=t0 - timedelta(days=1), text="past"),
            make_document(published_ts_utc=future, text="future"),
        ]
    )
    db_session.commit()

    prices = available_prices(db_session, "EUR/USD", t0)
    docs = available_documents(db_session, t0)

    assert all(bar.ts_utc <= t0 for bar in prices)
    assert all(doc.published_ts_utc < t0 for doc in docs)
    assert future not in [bar.ts_utc for bar in prices]
    assert "future" not in [doc.text for doc in docs]
