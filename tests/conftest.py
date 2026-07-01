from pathlib import Path

import pytest

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def sample_config_file() -> Path:
    return FIXTURES_DIR / "sample_config.yaml"
