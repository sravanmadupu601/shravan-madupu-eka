from __future__ import annotations

import math
from dataclasses import dataclass
from uuid import UUID

from app.retrieval.domain.models import RetrievalRequest, RetrievalResult


@dataclass(frozen=True)
class StoredVector:
    document_id: UUID
    chunk_id: UUID
    text: str
    vector: list[float]
    source: str | None = None
    page_number: int | None = None
    metadata: dict[str, str] | None = None


class InMemoryVectorRepository:
    """Local development adapter; it is not a replacement for pgvector."""

    def __init__(self, vectors: list[StoredVector] | None = None):
        self.vectors = vectors or []

    def search(self, request: RetrievalRequest) -> list[RetrievalResult]:
        if not self.vectors:
            return []
        query_norm = math.sqrt(sum(value * value for value in request.query_vector))
        if query_norm == 0:
            return []
        results = []
        for item in self.vectors:
            if len(item.vector) != len(request.query_vector):
                continue
            score = sum(a * b for a, b in zip(item.vector, request.query_vector))
            vector_norm = math.sqrt(sum(value * value for value in item.vector))
            score = score / (query_norm * vector_norm) if vector_norm else 0.0
            if score >= request.similarity_threshold:
                results.append(RetrievalResult(
                    item.document_id, item.chunk_id, item.text, score,
                    item.source, item.page_number, item.metadata or {},
                ))
        return sorted(results, key=lambda result: result.score, reverse=True)[:request.top_k]
