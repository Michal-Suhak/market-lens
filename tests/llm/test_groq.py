from unittest.mock import MagicMock

import httpx
import pytest
from groq import RateLimitError as GroqRateLimitError

from market_lens.llm.base import RateLimitError
from market_lens.llm.providers.groq import GroqClient


def test_groq_complete_returns_message_content():
    fake = MagicMock()
    fake.chat.completions.create.return_value.choices = [
        MagicMock(message=MagicMock(content="hawkish"))
    ]
    client = GroqClient("", client=fake)

    assert client.complete("read the statement") == "hawkish"
    fake.chat.completions.create.assert_called_once()


def test_groq_uses_configured_temperature():
    fake = MagicMock()
    fake.chat.completions.create.return_value.choices = [MagicMock(message=MagicMock(content="x"))]
    client = GroqClient("", temperature=0.5, client=fake)

    client.complete("p")

    assert fake.chat.completions.create.call_args.kwargs["temperature"] == 0.5


def test_groq_maps_rate_limit_error():
    fake = MagicMock()
    fake.chat.completions.create.side_effect = GroqRateLimitError(
        "rate limited",
        response=httpx.Response(429, request=httpx.Request("POST", "https://api.groq.com")),
        body=None,
    )
    client = GroqClient("", client=fake)

    with pytest.raises(RateLimitError):
        client.complete("prompt")
