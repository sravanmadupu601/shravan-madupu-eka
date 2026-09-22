from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.api.dependencies import get_orchestrator

router = APIRouter(prefix="/rag", tags=["RAG"])


class RAGQueryRequest(BaseModel):
    question: str = Field(min_length=1)
    top_k: int | None = Field(default=None, ge=1, le=100)
    filters: dict[str, str] = Field(default_factory=dict)


class CitationResponse(BaseModel):
    document_id: UUID
    chunk_id: UUID
    source: str | None = None
    page_number: int | None = None
    score: float


class RAGQueryResponse(BaseModel):
    answer: str
    citations: list[CitationResponse]
    retrieved_chunks: int


@router.post("/query", response_model=RAGQueryResponse)
def query(request: RAGQueryRequest, orchestrator=Depends(get_orchestrator)):
    try:
        answer, citations, count = orchestrator.execute(request.question, request.top_k, request.filters)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return RAGQueryResponse(
        answer=answer,
        citations=[CitationResponse(**citation.__dict__) for citation in citations],
        retrieved_chunks=count,
    )
