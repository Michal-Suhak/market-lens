.PHONY: init-db test lint format download-prices seed-fomc

PAIR ?= eurusd
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

download-prices:
	uv run python -c "from market_lens.collectors.download import download_histdata_m1; print(download_histdata_m1('$(PAIR)', '$(YEAR)', month=('$(MONTH)' or None)))"

seed-fomc:
	uv run python -c "from market_lens.config import load_config; from market_lens.storage import get_sessionmaker; from market_lens.collectors.fomc import fetch_fomc_events, load_fomc_events; s=get_sessionmaker()(); print('seeded', load_fomc_events(s, fetch_fomc_events(load_config().secrets.fred_api_key)), 'FOMC events')"
