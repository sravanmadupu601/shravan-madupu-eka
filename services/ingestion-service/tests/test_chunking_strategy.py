from app.infrastructure.chunking.semantic_chunker import SemanticChunker
from app.services.chunker_service import DocumentChunker
from app.services.ingestion_service import IngestionService


def test_fixed_strategy_is_selected(monkeypatch):
    from app.core.config import settings

    monkeypatch.setattr(settings, "chunking_strategy", "fixed")
    chunker = IngestionService._build_chunker()

    assert isinstance(chunker, DocumentChunker)


def test_semantic_strategy_is_selected(monkeypatch):
    from app.core.config import settings

    monkeypatch.setattr(settings, "chunking_strategy", "semantic")
    chunker = IngestionService._build_chunker()

    assert isinstance(chunker, SemanticChunker)


def test_unknown_strategy_is_rejected(monkeypatch):
    from app.core.config import settings

    monkeypatch.setattr(settings, "chunking_strategy", "unknown")

    try:
        IngestionService._build_chunker()
        assert False
    except ValueError as exc:
        assert "CHUNKING_STRATEGY" in str(exc)
