from tenacity import wait_none

from market_lens.llm.cache import CachingLLMClient, InMemoryLlmCache
from market_lens.llm.providers.groq import GROQ_MODEL, GroqClient
from market_lens.llm.retry import RetryingLLMClient


def test_provider_exposes_its_model():
    assert GroqClient("", client=object()).model == GROQ_MODEL


def test_wrappers_delegate_model_to_inner():
    provider = GroqClient("", model="custom-model", client=object())

    wrapped = CachingLLMClient(RetryingLLMClient(provider, wait=wait_none()), InMemoryLlmCache())

    assert wrapped.model == "custom-model"
