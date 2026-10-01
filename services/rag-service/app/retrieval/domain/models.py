from dataclasses import dataclass, field
from uuid import UUID


@dataclass(frozen=True)
class RetrievalRequest:
    query_vector: list[float]
    top_k: int
    similarity_threshold: float = 0.0
    filters: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class RetrievalResult:
    document_id: UUID
    chunk_id: UUID
    text: str
    score: float
    source: str | None = None
    page_number: int | None = None
    metadata: dict[str, str] = field(default_factory=dict)
