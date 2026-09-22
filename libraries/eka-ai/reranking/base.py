from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import Any


class Reranker(ABC):
    """Contract for optional retrieval reranking implementations."""

    @abstractmethod
    def rerank(self, query: str, candidates: Sequence[dict[str, Any]]) -> Sequence[dict[str, Any]]:
        raise NotImplementedError
