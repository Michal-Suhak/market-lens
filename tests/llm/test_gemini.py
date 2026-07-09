from unittest.mock import MagicMock

import pytest
from google.genai.errors import ClientError

from market_lens.llm.base import RateLimitError
from market_lens.llm.providers.gemini import GeminiClient


def test_gemini_complete_returns_text():
    fake = MagicMock()
    fake.models.generate_content.return_value.text = "dovish"
    client = GeminiClient("", client=fake)

    assert client.complete("read the statement") == "dovish"
    fake.models.generate_content.assert_called_once()


def test_gemini_maps_rate_limit_error():
    fake = MagicMock()
    fake.models.generate_content.side_effect = ClientError(429, {"error": {"message": "quota"}})
    client = GeminiClient("", client=fake)

    with pytest.raises(RateLimitError):
        client.complete("prompt")


def test_gemini_other_client_error_propagates():
    fake = MagicMock()
    fake.models.generate_content.side_effect = ClientError(400, {"error": {"message": "bad"}})
    client = GeminiClient("", client=fake)

    with pytest.raises(ClientError):
        client.complete("prompt")
