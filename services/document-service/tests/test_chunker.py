import pytest

from app.services.chunker_service import DocumentChunkerService


def test_chunker_returns_empty_list_for_empty_text():
    chunker = DocumentChunkerService(
        chunk_size=100,
        chunk_overlap=20,
    )

    result = chunker.chunk("")

    assert result == []


def test_chunker_creates_chunks():
    chunker = DocumentChunkerService(
        chunk_size=100,
        chunk_overlap=20,
    )

    text = "A " * 150

    result = chunker.chunk(text)

    assert len(result) > 1


def test_chunker_rejects_invalid_overlap():
    with pytest.raises(ValueError):
        DocumentChunkerService(
            chunk_size=100,
            chunk_overlap=100,
        )