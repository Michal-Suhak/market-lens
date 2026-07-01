from pathlib import Path

import pytest

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def histdata_csv() -> Path:
    return FIXTURES_DIR / "eurusd_m1_sample.csv"
