from market_lens.measurement.frame import build_frame


def test_build_frame_joins_prediction_and_outcome(
    db_session, make_event, make_prediction, make_outcome
):
    event = make_event()
    db_session.add(event)
    db_session.add(make_prediction(event=event, direction="up", score=0.4, model="m"))
    db_session.add(make_outcome(event=event, pair="EUR/USD", realized_direction="up", ret_1h=0.001))
    db_session.commit()

    rows = build_frame(db_session, pair="EUR/USD")

    assert len(rows) == 1
    row = rows[0]
    assert row.event_id == event.id
    assert row.direction == "up"
    assert row.score == 0.4
    assert row.realized_direction == "up"
    assert row.ret_1h == 0.001
    assert row.surprise == event.surprise


def test_build_frame_excludes_prediction_without_outcome(db_session, make_event, make_prediction):
    event = make_event()
    db_session.add(event)
    db_session.add(make_prediction(event=event))
    db_session.commit()

    rows = build_frame(db_session, pair="EUR/USD")

    assert rows == []


def test_build_frame_excludes_outcome_without_prediction(db_session, make_event, make_outcome):
    event = make_event()
    db_session.add(event)
    db_session.add(make_outcome(event=event, pair="EUR/USD"))
    db_session.commit()

    rows = build_frame(db_session, pair="EUR/USD")

    assert rows == []


def test_build_frame_filters_by_pair(db_session, make_event, make_prediction, make_outcome):
    event = make_event()
    db_session.add(event)
    db_session.add(make_prediction(event=event))
    db_session.add(make_outcome(event=event, pair="GBP/USD"))
    db_session.commit()

    assert build_frame(db_session, pair="EUR/USD") == []
    assert len(build_frame(db_session, pair="GBP/USD")) == 1


def test_build_frame_filters_by_model(db_session, make_event, make_prediction, make_outcome):
    event = make_event()
    db_session.add(event)
    db_session.add(make_prediction(event=event, model="gemini"))
    db_session.add(make_outcome(event=event, pair="EUR/USD"))
    db_session.commit()

    assert len(build_frame(db_session, pair="EUR/USD", model="gemini")) == 1
    assert build_frame(db_session, pair="EUR/USD", model="groq") == []


def test_build_frame_preserves_gap_returns(db_session, make_event, make_prediction, make_outcome):
    event = make_event()
    db_session.add(event)
    db_session.add(make_prediction(event=event))
    db_session.add(make_outcome(event=event, pair="EUR/USD", ret_4h=None, realized_direction=None))
    db_session.commit()

    row = build_frame(db_session, pair="EUR/USD")[0]

    assert row.ret_4h is None
    assert row.realized_direction is None
