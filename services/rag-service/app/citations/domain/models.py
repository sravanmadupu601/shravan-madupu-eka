from dataclasses import dataclass
from uuid import UUID

from app.retrieval.domain.models import RetrievalResult


@dataclass(frozen=True)
class Citation:
    document_id: UUID
    chunk_id: UUID
    source: str | None
    page_number: int | None
    score: float


class CitationBuilder:
    def build(self, results: list[RetrievalResult]) -> list[Citation]:
        return [Citation(r.document_id, r.chunk_id, r.source, r.page_number, r.score) for r in results]
