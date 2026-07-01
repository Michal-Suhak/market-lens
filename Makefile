.PHONY: init-db test lint format download-prices

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
