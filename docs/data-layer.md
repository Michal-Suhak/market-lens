# Data layer

How to fetch the source data and load it into the database. Every source has a single `make`
command that goes from the source straight into the database. All timestamps are stored in UTC.

## Prerequisites

1. Install dependencies: `uv sync`
2. Copy `.env.example` to `.env` and fill in the keys:
   - `FRED_API_KEY` — free key from https://fredaccount.stlouisfed.org (needed for FOMC events and
     statements).
   - `DATABASE_URL` — defaults to a local SQLite file (`data/market_lens.db`).
3. Create the tables: `make init-db`

## Prices — HistData M1

FX 1-minute OHLC bars from HistData.com (bid quotes, treated as mid). Source timestamps are in EST
without daylight saving and are converted to UTC on load. Data lags real time by a few days.

```bash
make import-prices PAIR=EUR/USD YEAR=2025            # a closed year, one file
make import-prices PAIR=EUR/USD YEAR=2026 MONTH=6    # the current year, per month
```

This downloads the CSV into `data/prices/` and loads the bars into the `prices` table.

## FOMC events

FOMC meeting dates come from the St. Louis Fed (FRED release 101, includes holds); the target rate
(`actual`) comes from the `DFEDTARU` series. Each event is timestamped at 14:00 ET (2:00 PM),
converted to UTC. Needs `FRED_API_KEY`.

```bash
make seed-fomc
```

Consensus forecasts are not freely available, so `surprise = actual - forecast` is filled in only
for events where a forecast is supplied.

## FED statements

FOMC statement text is fetched from federalreserve.gov and loaded into the `documents` table with
`institution=FED`, `doc_type=FOMC`, and the same 14:00 ET (UTC) publication timestamp as the event.
The meeting dates are taken from FRED, so this also needs `FRED_API_KEY`.

```bash
make fetch-statements YEAR=2025
```

## Notes

- Re-running an import for data already in the database fails on the unique/primary keys — import
  into a fresh database or a range that has not been imported yet.
- `make test`, `make lint`, `make format` run the test suite, linter, and formatter.
