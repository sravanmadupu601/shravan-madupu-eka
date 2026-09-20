import pytest

from app.services.chunker_service import DocumentChunker


def test_chunker_empty_text():
    assert DocumentChunker(100, 20).chunk("") == []


def test_chunker_overlap_and_metadata():
    chunks = DocumentChunker(20, 5).chunk("A " * 30)
    assert len(chunks) > 1
    assert all(chunk.character_count == len(chunk.content) for chunk in chunks)
    assert all(chunk.token_count > 0 for chunk in chunks)
    assert chunks[0].content[-5:] == chunks[1].content[:5]


def test_chunker_rejects_invalid_overlap():
    with pytest.raises(ValueError):
        DocumentChunker(100, 100)
