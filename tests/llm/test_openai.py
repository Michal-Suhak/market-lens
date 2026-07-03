from unittest.mock import MagicMock

import httpx
import pytest
from openai import RateLimitError as OpenAIRateLimitError

from market_lens.llm.base import RateLimitError
from market_lens.llm.providers.openai import OpenAIClient


def test_openai_complete_returns_message_content():
    fake = MagicMock()
    fake.chat.completions.create.return_value.choices = [
        MagicMock(message=MagicMock(content="neutral"))
    ]
    client = OpenAIClient("", client=fake)

    assert client.complete("read the statement") == "neutral"
    fake.chat.completions.create.assert_called_once()


def test_openai_maps_rate_limit_error():
    fake = MagicMock()
    fake.chat.completions.create.side_effect = OpenAIRateLimitError(
        "rate limited",
        response=httpx.Response(429, request=httpx.Request("POST", "https://api.openai.com")),
        body=None,
    )
    client = OpenAIClient("", client=fake)

    with pytest.raises(RateLimitError):
        client.complete("prompt")
