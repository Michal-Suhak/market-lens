import pytest
from pydantic import ValidationError

from market_lens.llm.base import LLMClient
from market_lens.prediction.generate import generate_prediction
from market_lens.prediction.schema import PredictionOutput

VALID = '{"tone": "hawkish", "direction": "down", "confidence": 0.8, "score": -0.6}'
OUT_OF_RANGE = '{"tone": "hawkish", "direction": "down", "confidence": 5, "score": -0.6}'


class _ScriptedClient(LLMClient):
    def __init__(self, *responses: str):
        self._responses = responses
        self.calls = 0

    def complete(self, prompt: str) -> str:
        response = self._responses[min(self.calls, len(self._responses) - 1)]
        self.calls += 1
        return response


def test_returns_validated_output():
    llm = _ScriptedClient(VALID)

    out = generate_prediction(llm, "prompt")

    assert isinstance(out, PredictionOutput)
    assert out.direction == "down"
    assert llm.calls == 1


def test_retries_invalid_json_then_succeeds():
    llm = _ScriptedClient("not json at all", VALID)

    out = generate_prediction(llm, "prompt", max_attempts=3)

    assert out.tone == "hawkish"
    assert llm.calls == 2


def test_retries_out_of_range_value_then_succeeds():
    llm = _ScriptedClient(OUT_OF_RANGE, VALID)

    out = generate_prediction(llm, "prompt", max_attempts=3)

    assert out.confidence == 0.8
    assert llm.calls == 2


def test_rejects_after_exhausting_attempts():
    llm = _ScriptedClient("garbage")

    with pytest.raises(ValidationError):
        generate_prediction(llm, "prompt", max_attempts=3)

    assert llm.calls == 3


def test_succeeds_on_the_last_allowed_attempt():
    llm = _ScriptedClient("bad", "bad", VALID)

    out = generate_prediction(llm, "prompt", max_attempts=3)

    assert out.tone == "hawkish"
    assert llm.calls == 3


def test_max_attempts_one_does_not_retry():
    llm = _ScriptedClient("garbage")

    with pytest.raises(ValidationError):
        generate_prediction(llm, "prompt", max_attempts=1)

    assert llm.calls == 1
