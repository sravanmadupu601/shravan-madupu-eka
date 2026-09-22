from typing import Protocol

from app.reranking.domain.models import RerankRequest, RerankResult


class Reranker(Protocol):
    def rerank(self, request: RerankRequest) -> RerankResult:
        ...
