.PHONY: init-db test lint format import-prices seed-fomc fetch-statements compute-outcomes build-rag-index predict

PAIR ?= EUR/USD
YEAR ?= 2025
MONTH ?=

init-db:
	uv run python -c "from market_lens.storage import init_db; init_db()"

test:
	uv run pytest

lint:
	uv run ruff check .

format:
	uv run black .

import-prices:
	uv run python -c "from market_lens.storage import get_sessionmaker; from market_lens.collectors.prices import import_histdata_m1; s=get_sessionmaker()(); print('imported', import_histdata_m1(s, '$(PAIR)', '$(YEAR)', month=('$(MONTH)' or None)), 'bars')"

seed-fomc:
	uv run python -c "from market_lens.config import load_config; from market_lens.storage import get_sessionmaker; from market_lens.collectors.fomc import fetch_fomc_events, load_fomc_events; s=get_sessionmaker()(); print('seeded', load_fomc_events(s, fetch_fomc_events(load_config().secrets.fred_api_key)), 'FOMC events')"

fetch-statements:
	uv run python -c "from market_lens.config import load_config; from market_lens.storage import get_sessionmaker; from market_lens.collectors.fomc import fetch_fomc_dates; from market_lens.collectors.documents import load_fed_statements; dates=[d for d in fetch_fomc_dates(load_config().secrets.fred_api_key) if d.year==int('$(YEAR)')]; s=get_sessionmaker()(); print('loaded', load_fed_statements(s, dates), 'statements')"

compute-outcomes:
	uv run python -c "from market_lens.config import load_config; from market_lens.storage import get_sessionmaker; from market_lens.outcomes.compute import compute_all_outcomes; cfg=load_config(); s=get_sessionmaker()(); print('computed', compute_all_outcomes(s, cfg.pairs), 'outcomes')"

build-rag-index:
	uv run python -c "from market_lens.storage import get_sessionmaker; from market_lens.rag.qdrant import get_client; from market_lens.rag.embedder import Embedder; from market_lens.rag.indexing import index_all_documents; s=get_sessionmaker()(); print('indexed', index_all_documents(get_client(), Embedder(), s), 'points')"

predict:
	uv run python -c "from market_lens.config import load_config; from market_lens.storage import get_sessionmaker; from market_lens.llm.factory import make_llm_client; from market_lens.llm.cache import CachingLLMClient, SqlLlmCache; from market_lens.llm.retry import RetryingLLMClient; from market_lens.rag.qdrant import get_client; from market_lens.rag.embedder import Embedder; from market_lens.prediction.pipeline import predict_all_events; cfg=load_config(); s=get_sessionmaker()(); llm=CachingLLMClient(RetryingLLMClient(make_llm_client(cfg)), SqlLlmCache(s)); print('predicted', predict_all_events(s, get_client(), Embedder(), llm, pair=cfg.pairs[0]), 'events')"
