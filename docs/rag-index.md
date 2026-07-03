# Building the RAG index

The retrieval layer indexes central-bank documents into Qdrant so a prediction can pull similar
past statements — filtered strictly by institution.

## Prerequisites

- Documents loaded into the database (see [data-layer.md](data-layer.md), `make fetch-statements`).
- Qdrant running:

  ```bash
  docker compose up -d qdrant
  ```

  It listens on `QDRANT_URL` (default `http://localhost:6333`).

## Build the index

```bash
make build-rag-index
```

This chunks every stored document, embeds the chunks locally with `bge-small-en-v1.5` (CPU), and
upserts them into the `documents` collection with metadata (`institution`, `doc_type`, `date`).

- Re-running is safe: point ids are deterministic, so it refreshes existing points instead of
  duplicating them.
- The first run downloads the embedding model once into the local cache.

## How retrieval stays isolated

Search always requires an `institution`, applied as a hard filter **before** the vector search. A
query scoped to `FED` can never return `ECB` chunks — even when an ECB chunk is semantically closer
— so a prediction about one institution is grounded only in that institution's documents.
