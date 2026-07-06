from __future__ import annotations

from collections.abc import Iterable


def build_prompt(statement: str, context: Iterable[str], *, pair: str) -> str:
    context_block = "\n\n".join(context) or "(none)"
    return (
        "You read central-bank statements and predict the short-term FX reaction. "
        "Respond with ONLY a JSON object matching this schema - no prose, no BUY/SELL advice:\n"
        '{"tone": "hawkish|dovish|neutral", "direction": "up|down|flat", '
        '"confidence": <0..1>, "score": <-1..1 signed conviction>}\n'
        f"direction is where {pair} moves in the hours after the release; up means {pair} rises. "
        "confidence is how sure you are; score is signed conviction from -1 (strong down) to "
        "+1 (strong up).\n\n"
        f"Similar earlier statements:\n{context_block}\n\n"
        f"Statement to assess:\n{statement}"
    )
