from market_lens.prediction.prompt import build_prompt


def test_prompt_includes_statement():
    prompt = build_prompt("FOMC held rates steady.", [], pair="EUR/USD")

    assert "FOMC held rates steady." in prompt


def test_prompt_includes_all_context_chunks():
    prompt = build_prompt("statement", ["prior note A", "prior note B"], pair="EUR/USD")

    assert "prior note A" in prompt
    assert "prior note B" in prompt


def test_prompt_mentions_the_pair():
    prompt = build_prompt("statement", [], pair="GBP/USD")

    assert "GBP/USD" in prompt


def test_prompt_specifies_all_schema_fields():
    prompt = build_prompt("statement", [], pair="EUR/USD")

    for field in ('"tone"', '"direction"', '"confidence"', '"score"'):
        assert field in prompt


def test_prompt_forbids_prose_and_trade_advice():
    prompt = build_prompt("statement", [], pair="EUR/USD")

    assert "JSON" in prompt
    assert "BUY/SELL" in prompt


def test_prompt_handles_empty_context():
    prompt = build_prompt("statement", [], pair="EUR/USD")

    assert "(none)" in prompt
