from market_lens.rag.embedder import EMBEDDING_DIM


def test_embed_returns_expected_dimension_and_is_stable(embedder):
    vectors = embedder.embed(["The Committee decided to maintain the target range."])
    again = embedder.embed(["The Committee decided to maintain the target range."])

    assert len(vectors) == 1
    assert len(vectors[0]) == EMBEDDING_DIM
    assert vectors[0] == again[0]


def test_embed_batches_multiple_texts(embedder):
    vectors = embedder.embed(["first statement", "second statement"])

    assert len(vectors) == 2
    assert all(len(vector) == EMBEDDING_DIM for vector in vectors)
