from dataclasses import dataclass

from app.retrieval.domain.models import RetrievalResult


@dataclass(frozen=True)
class Context:
    text: str
    chunks: list[RetrievalResult]
    character_count: int


@dataclass(frozen=True)
class ContextRequest:
    results: list[RetrievalResult]
    max_characters: int
