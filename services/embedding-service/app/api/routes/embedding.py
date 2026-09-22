from uuid import UUID

from fastapi import APIRouter, Depends

from app.api.dependencies import get_embedding_service
from app.application.services.embedding_service import EmbeddingApplicationService
from app.schemas import EmbeddingItem, EmbeddingMetadataResponse, EmbeddingRequest, EmbeddingResponse

router = APIRouter(prefix="/embeddings", tags=["Embeddings"])


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
