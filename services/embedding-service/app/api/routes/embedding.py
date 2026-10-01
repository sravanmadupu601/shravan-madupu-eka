from uuid import UUID

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.api.dependencies import get_embedding_service
from app.application.services.embedding_service import EmbeddingApplicationService
from app.schemas import EmbeddingItem, EmbeddingMetadataResponse, EmbeddingRequest, EmbeddingResponse

router = APIRouter(prefix="/embeddings", tags=["Embeddings"])


class EmbeddingSearchRequest(BaseModel):
    query_embedding: list[float] = Field(min_length=1)
    top_k: int = Field(default=5, ge=1, le=100)
    similarity_threshold: float | None = Field(default=None, ge=-1, le=1)
    document_id: UUID | None = None
    model_name: str | None = None
    model_version: str | None = None


class EmbeddingSearchItem(BaseModel):
    document_id: UUID
    chunk_id: UUID
    model_name: str
    model_version: str
    dimension: int
    distance: float
    similarity: float


def _item(embedding) -> EmbeddingItem:
    return EmbeddingItem(
        id=embedding.id,
        chunk_id=embedding.chunk_id,
        model_name=embedding.model_name,
        model_version=embedding.model_version,
        dimension=embedding.dimension,
        created_at=embedding.created_at,
    )


@router.post("", response_model=EmbeddingResponse)
def create_embeddings(
    request: EmbeddingRequest,
    service: EmbeddingApplicationService = Depends(get_embedding_service),
):
    embeddings = service.embed_chunks(
        request.document_id,
        [(chunk.chunk_id, chunk.text) for chunk in request.chunks],
    )
    model_name = embeddings[0].model_name
    model_version = embeddings[0].model_version
    dimension = embeddings[0].dimension
    return EmbeddingResponse(
        document_id=request.document_id,
        embeddings=[_item(embedding) for embedding in embeddings],
        status="COMPLETED",
        model_name=model_name,
        model_version=model_version,
        dimension=dimension,
    )


@router.get("/{document_id}", response_model=EmbeddingMetadataResponse)
def get_embeddings(
    document_id: UUID,
    service: EmbeddingApplicationService = Depends(get_embedding_service),
):
    embeddings = service.list_document_embeddings(document_id)
    return EmbeddingMetadataResponse(
        document_id=document_id,
        embeddings=[_item(embedding) for embedding in embeddings],
        count=len(embeddings),
    )


@router.post("/search", response_model=list[EmbeddingSearchItem])
def search_embeddings(
    request: EmbeddingSearchRequest,
    service: EmbeddingApplicationService = Depends(get_embedding_service),
):
    results = service.search_similar(
        request.query_embedding,
        request.top_k,
        request.similarity_threshold,
        {
            key: value
            for key, value in {
                "document_id": str(request.document_id) if request.document_id else None,
                "model_name": request.model_name,
                "model_version": request.model_version,
            }.items()
            if value is not None
        },
    )
    return [
        EmbeddingSearchItem(
            document_id=result.embedding.document_id,
            chunk_id=result.embedding.chunk_id,
            model_name=result.embedding.model_name,
            model_version=result.embedding.model_version,
            dimension=result.embedding.dimension,
            distance=result.distance,
            similarity=result.similarity,
        )
        for result in results
    ]
