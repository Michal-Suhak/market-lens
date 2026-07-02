from __future__ import annotations

from collections.abc import Iterable

from fastembed import TextEmbedding

# Swap for another 384-dim model (e.g. all-MiniLM-L6-v2) if retrieval quality is not good enough.
MODEL_NAME = "BAAI/bge-small-en-v1.5"
EMBEDDING_DIM = 384


class Embedder:
    def __init__(self, model_name: str = MODEL_NAME):
        self._model = TextEmbedding(model_name=model_name)

    def embed(self, texts: Iterable[str]) -> list[list[float]]:
        return [vector.tolist() for vector in self._model.embed(list(texts))]
