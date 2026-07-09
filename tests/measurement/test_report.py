import json
from datetime import datetime, timezone

from market_lens.measurement.report import build_report, write_frame_csv, write_json

UTC = timezone.utc


def _seed(db_session, make_event, make_prediction, make_outcome):
    first = make_event(ts_utc=datetime(2026, 1, 28, 19, 0, tzinfo=UTC), surprise=0.1)
    second = make_event(ts_utc=datetime(2026, 3, 18, 18, 0, tzinfo=UTC), surprise=-0.1)
    db_session.add_all([first, second])
    db_session.add(make_prediction(event=first, direction="up", score=0.2, model="m"))
    db_session.add(make_prediction(event=second, direction="down", score=0.8, model="m"))
    db_session.add(make_outcome(event=first, pair="EUR/USD", realized_direction="up", ret_1h=0.001))
    db_session.add(
        make_outcome(event=second, pair="EUR/USD", realized_direction="up", ret_1h=0.002)
    )
    db_session.commit()


def test_build_report_has_all_metric_sections(
    db_session, make_event, make_prediction, make_outcome
):
    _seed(db_session, make_event, make_prediction, make_outcome)

    report = build_report(db_session, pair="EUR/USD", model="m")

    assert report["n"] == 2
    assert report["accuracy"]["accuracy"] is not None
    assert report["information_coefficient"]["ic"] is not None
    assert report["calibration"]["brier"] is not None
    assert report["lift"]["surprise_sign"]["lift"] is not None
    assert report["lift"]["coin_flip"]["lift"] is not None


def test_write_json_round_trips(tmp_path, db_session, make_event, make_prediction, make_outcome):
    _seed(db_session, make_event, make_prediction, make_outcome)
    report = build_report(db_session, pair="EUR/USD", model="m")

    path = write_json(report, tmp_path / "report.json")
    loaded = json.loads(path.read_text())

    assert loaded["accuracy"]["accuracy"] == report["accuracy"]["accuracy"]
    assert loaded["calibration"]["brier"] == report["calibration"]["brier"]
    assert loaded["lift"]["surprise_sign"]["lift"] == report["lift"]["surprise_sign"]["lift"]


def test_write_frame_csv_writes_a_row_per_event(
    tmp_path, db_session, make_event, make_prediction, make_outcome
):
    _seed(db_session, make_event, make_prediction, make_outcome)

    path = write_frame_csv(db_session, tmp_path / "frame.csv", pair="EUR/USD", model="m")
    lines = path.read_text().splitlines()

    assert lines[0].startswith("event_id,model,pair,ts_utc")
    assert len(lines) == 3
