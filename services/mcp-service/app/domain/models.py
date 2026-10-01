from pydantic import BaseModel, Field


class Citation(BaseModel):
    document_id: str
    chunk_id: str
    source: str | None = None
    page_number: int | None = None
    score: float


class KnowledgeSearchResult(BaseModel):
    answer: str
    citations: list[Citation] = Field(default_factory=list)
    retrieved_chunks: int = Field(ge=0)


class DocumentRecord(BaseModel):
    id: str
    filename: str
    content_type: str
    file_size: int
    checksum: str
    status: str
    version: int
    created_at: str
    updated_at: str


class DocumentPage(BaseModel):
    documents: list[DocumentRecord]
    total: int
    limit: int
    offset: int


class DownstreamHealth(BaseModel):
    service: str
    available: bool
    status_code: int | None = None
    status: str
