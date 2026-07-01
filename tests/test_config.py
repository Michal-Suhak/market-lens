from pathlib import Path

from market_lens.config import Secrets, load_config


def test_load_config_from_yaml(sample_config_file):
    cfg = load_config(sample_config_file)
    assert cfg.pairs == ["EUR/USD", "GBP/USD"]
    assert cfg.windows_hours == [1, 4, 24]
    assert cfg.paths.prices_dir == Path("data/prices")


def test_load_config_default_path():
    cfg = load_config()
    assert "EUR/USD" in cfg.pairs
    assert cfg.windows_hours == [1, 4, 24]


def test_secrets_default_to_empty():
    secrets = Secrets(_env_file=None)
    assert secrets.groq_api_key == ""
    assert secrets.gemini_api_key == ""
