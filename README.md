# market-lens

A measurement instrument for central-bank statements (starting with the FOMC): it reads the
statement, predicts FX direction via an LLM, and measures whether that prediction carries real
information about the subsequent price move — versus simple baselines (bare numeric surprise,
coin flip).

This is **not** an autotrader. It doesn't make trading decisions for profit. It answers a
research question: does an LLM's reading of a central-bank communication (tone, RAG context)
carry information about what the exchange rate will do afterwards — and does it carry *more*
information than the bare numeric surprise or a coin flip?

## Status

Early stage — the data layer (events, documents, prices) is in place; the prediction and
measurement layers are not built yet.

## Getting started

Requires Python 3.13 and [`uv`](https://docs.astral.sh/uv/).

```bash
uv sync
uv run pytest
```

Lint / format:

```bash
uv run ruff check .
uv run black --check .
```

## Data

See [docs/data-layer.md](docs/data-layer.md) for how to fetch source data (FX prices, FOMC events,
FED statements) and load it into the database, and [docs/rag-index.md](docs/rag-index.md) for
building the RAG index.

## Project layout

```
src/market_lens/
  collectors/   # fetching events, documents, prices
  storage/      # SQLAlchemy models (events, documents, prices, predictions, outcomes)
  replay/       # point-in-time replay
  rag/          # vector store, embeddings, metadata filtering
  features/     # surprise = actual - forecast (optional)
  llm/          # LLM clients, structured output, backoff, cache
  prediction/   # tone -> direction + confidence
  outcomes/     # ret +1h/+4h/+24h on mid price
  measurement/  # accuracy, Information Coefficient, calibration, event-study, lift <- the core
  forwardtest/  # loop over fresh, out-of-sample events
  api/          # FastAPI + dashboard
tests/
data/
```
