from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from market_lens.utils import add_hours, parse_utc, to_utc

UTC = timezone.utc


def test_naive_assumed_utc():
    result = to_utc(datetime(2026, 1, 28, 19, 0))

    assert result == datetime(2026, 1, 28, 19, 0, tzinfo=UTC)
    assert result.tzinfo == UTC


def test_aware_converted_to_utc():
    ny = ZoneInfo("America/New_York")  # EST = UTC-5 in January

    result = to_utc(datetime(2026, 1, 28, 14, 0, tzinfo=ny))

    assert result == datetime(2026, 1, 28, 19, 0, tzinfo=UTC)


def test_parse_iso():
    assert parse_utc("2026-01-28T19:00:00") == datetime(2026, 1, 28, 19, 0, tzinfo=UTC)


def test_parse_custom_format():
    result = parse_utc("20260128 190000", fmt="%Y%m%d %H%M%S")

    assert result == datetime(2026, 1, 28, 19, 0, tzinfo=UTC)


def test_add_hours_in_utc():
    t0 = datetime(2026, 1, 28, 19, 0, tzinfo=UTC)

    assert add_hours(t0, 4) == datetime(2026, 1, 28, 23, 0, tzinfo=UTC)


def test_add_hours_across_dst_boundary():
    ny = ZoneInfo("America/New_York")
    t0 = to_utc(datetime(2026, 3, 8, 1, 30, tzinfo=ny))  # 01:30 EST, before spring-forward
    assert t0 == datetime(2026, 3, 8, 6, 30, tzinfo=UTC)

    result = add_hours(t0, 4)

    assert result == datetime(2026, 3, 8, 10, 30, tzinfo=UTC)
    assert result.astimezone(ny) == datetime(2026, 3, 8, 6, 30, tzinfo=ny)  # wall clock jumped 5h
