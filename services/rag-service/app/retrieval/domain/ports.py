from typing import Protocol

from app.retrieval.domain.models import RetrievalRequest, RetrievalResult


class VectorRepository(Protocol):
    def search(self, request: RetrievalRequest) -> list[RetrievalResult]:
        ...


class Retriever(Protocol):
    def retrieve(self, request: RetrievalRequest) -> list[RetrievalResult]:
        ...
