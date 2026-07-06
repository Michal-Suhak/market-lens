import pytest
from pydantic import ValidationError

from market_lens.prediction.schema import PredictionOutput

VALID = {"tone": "hawkish", "direction": "down", "confidence": 0.8, "score": -0.6}


def test_valid_prediction_output():
    out = PredictionOutput(**VALID)

    assert (out.tone, out.direction, out.confidence, out.score) == ("hawkish", "down", 0.8, -0.6)


@pytest.mark.parametrize("tone", ["hawkish", "dovish", "neutral"])
def test_accepts_each_tone(tone):
    assert PredictionOutput(**{**VALID, "tone": tone}).tone == tone


@pytest.mark.parametrize("direction", ["up", "down", "flat"])
def test_accepts_each_direction(direction):
    assert PredictionOutput(**{**VALID, "direction": direction}).direction == direction


@pytest.mark.parametrize("confidence", [0.0, 1.0])
def test_accepts_confidence_bounds(confidence):
    assert PredictionOutput(**{**VALID, "confidence": confidence}).confidence == confidence


@pytest.mark.parametrize("score", [-1.0, 1.0])
def test_accepts_score_bounds(score):
    assert PredictionOutput(**{**VALID, "score": score}).score == score


@pytest.mark.parametrize("confidence", [-0.01, 1.5])
def test_rejects_confidence_out_of_range(confidence):
    with pytest.raises(ValidationError):
        PredictionOutput(**{**VALID, "confidence": confidence})


@pytest.mark.parametrize("score", [-1.5, 2.0])
def test_rejects_score_out_of_range(score):
    with pytest.raises(ValidationError):
        PredictionOutput(**{**VALID, "score": score})


def test_rejects_invalid_tone():
    with pytest.raises(ValidationError):
        PredictionOutput(**{**VALID, "tone": "bullish"})


def test_rejects_invalid_direction():
    with pytest.raises(ValidationError):
        PredictionOutput(**{**VALID, "direction": "sideways"})


def test_rejects_missing_field():
    with pytest.raises(ValidationError):
        PredictionOutput(tone="hawkish", direction="down", confidence=0.5)


def test_rejects_non_numeric_score():
    with pytest.raises(ValidationError):
        PredictionOutput(**{**VALID, "score": "high"})
