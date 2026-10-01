from dataclasses import dataclass

from app.retrieval.domain.models import RetrievalResult


@dataclass(frozen=True)
class RerankRequest:
    results: list[RetrievalResult]


@dataclass(frozen=True)
class RerankResult:
    results: list[RetrievalResult]
