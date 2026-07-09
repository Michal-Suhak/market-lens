import pytest
from pydantic import BaseModel, ValidationError

from market_lens.llm.base import LLMClient


class _Answer(BaseModel):
    direction: str
    confidence: float


class _StubClient(LLMClient):
    def __init__(self, response: str):
        self._response = response

    def complete(self, prompt: str) -> str:
        return self._response


def test_structured_returns_validated_object():
    client = _StubClient('{"direction": "up", "confidence": 0.8}')

    result = client.structured("predict", _Answer)

    assert isinstance(result, _Answer)
    assert result.direction == "up"
    assert result.confidence == 0.8


def test_structured_rejects_invalid_output():
    client = _StubClient("not json at all")

    with pytest.raises(ValidationError):
        client.structured("predict", _Answer)
