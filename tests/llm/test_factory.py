import pytest
from pydantic import ValidationError

from market_lens.config import Config, Paths, Secrets
from market_lens.llm.factory import make_llm_client
from market_lens.llm.providers import GeminiClient, GroqClient, OpenAIClient


def _config(provider: str) -> Config:
    return Config(
        pairs=["EUR/USD"],
        windows_hours=[1, 4, 24],
        paths=Paths(data_dir="data", prices_dir="data/prices", documents_dir="data/documents"),
        llm_provider=provider,
        secrets=Secrets(groq_api_key="dummy", gemini_api_key="dummy", openai_api_key="dummy"),
    )


def test_factory_selects_groq():
    assert isinstance(make_llm_client(_config("groq")), GroqClient)


def test_factory_selects_gemini():
    assert isinstance(make_llm_client(_config("gemini")), GeminiClient)


def test_factory_selects_openai():
    assert isinstance(make_llm_client(_config("openai")), OpenAIClient)


def test_config_rejects_unknown_provider():
    with pytest.raises(ValidationError):
        _config("anthropic")
