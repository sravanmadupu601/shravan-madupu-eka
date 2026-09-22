from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class ChunkInput(BaseModel):
    chunk_id: UUID
    text: str = Field(min_length=1)


class EmbeddingRequest(BaseModel):
    document_id: UUID
    chunks: list[ChunkInput] = Field(min_length=1)

    @field_validator("chunks")
    @classmethod
    def chunk_ids_must_be_unique(cls, chunks: list[ChunkInput]) -> list[ChunkInput]:
        chunk_ids = [chunk.chunk_id for chunk in chunks]
        if len(chunk_ids) != len(set(chunk_ids)):
            raise ValueError("chunk_id values must be unique within a request.")
        return chunks


class EmbeddingItem(BaseModel):
    id: UUID
    chunk_id: UUID
    model_name: str
    model_version: str
    dimension: int
    created_at: datetime | None = None


class EmbeddingResponse(BaseModel):
    document_id: UUID
    embeddings: list[EmbeddingItem]
    status: str
    model_name: str
    model_version: str
    dimension: int


class EmbeddingMetadataResponse(BaseModel):
    document_id: UUID
    embeddings: list[EmbeddingItem]
    count: int
