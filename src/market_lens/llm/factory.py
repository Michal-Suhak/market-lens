from __future__ import annotations

from market_lens.config import Config
from market_lens.llm.base import LLMClient
from market_lens.llm.providers import GeminiClient, GroqClient, OpenAIClient


def make_llm_client(config: Config) -> LLMClient:
    temperature = config.llm_temperature
    if config.llm_provider == "groq":
        return GroqClient(config.secrets.groq_api_key, temperature=temperature)
    if config.llm_provider == "gemini":
        return GeminiClient(config.secrets.gemini_api_key, temperature=temperature)
    if config.llm_provider == "openai":
        return OpenAIClient(config.secrets.openai_api_key, temperature=temperature)
    raise ValueError(f"unknown llm provider: {config.llm_provider!r}")
