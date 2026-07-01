.PHONY: init-db test lint format

init-db:
	uv run python -c "from market_lens.storage import init_db; init_db()"

test:
	uv run pytest

lint:
	uv run ruff check .

format:
	uv run black .
