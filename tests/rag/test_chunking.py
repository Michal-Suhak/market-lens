import pytest

from market_lens.rag.chunking import chunk_document, chunk_text


def test_chunk_text_overlapping_windows():
    text = " ".join(str(i) for i in range(10))

    chunks = chunk_text(text, size=4, overlap=1)

    assert chunks == ["0 1 2 3", "3 4 5 6", "6 7 8 9"]


def test_chunk_text_short_text_is_one_chunk():
    assert chunk_text("short doc", size=10, overlap=2) == ["short doc"]


def test_chunk_text_empty_returns_no_chunks():
    assert chunk_text("", size=10, overlap=2) == []


def test_chunk_text_rejects_overlap_not_smaller_than_size():
    with pytest.raises(ValueError):
        chunk_text("some text", size=4, overlap=4)


def test_chunk_document_carries_doc_id_and_index(db_session, make_document):
    doc = make_document(text=" ".join(str(i) for i in range(10)))
    db_session.add(doc)
    db_session.commit()

    chunks = chunk_document(doc, size=4, overlap=1)

    assert len(chunks) == 3
    assert all(chunk.doc_id == doc.id for chunk in chunks)
    assert [chunk.index for chunk in chunks] == [0, 1, 2]
