from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class Embedding:
    id: UUID
    document_id: UUID
    chunk_id: UUID
    vector: list[float]
    model_name: str
    model_version: str
    dimension: int
    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass(frozen=True)
class EmbeddingSearchResult:
    embedding: Embedding
    distance: float
    similarity: float
