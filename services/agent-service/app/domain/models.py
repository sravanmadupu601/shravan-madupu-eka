from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field, field_validator


class Intent(StrEnum):
    KNOWLEDGE = "KNOWLEDGE"
    BUSINESS_DATA = "BUSINESS_DATA"
    KNOWLEDGE_AND_BUSINESS_DATA = "KNOWLEDGE_AND_BUSINESS_DATA"
    GENERAL = "GENERAL"


class AgentRequest(BaseModel):
    query: str = Field(min_length=1, max_length=4000)

    @field_validator("query")
    @classmethod
    def query_must_contain_text(cls, query: str) -> str:
        query = query.strip()
        if not query:
            raise ValueError("query must contain non-whitespace text")
        return query


class Citation(BaseModel):
    source: str
    text: str | None = None
    document_id: str | None = None
    chunk_id: str | None = None
    page_number: int | None = None
    score: float | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class AgentResponse(BaseModel):
    answer: str
    intent: Intent
    route: str
    citations: list[Citation] = Field(default_factory=list)
    tools_used: list[str] = Field(default_factory=list)
    retry_count: int = 0
    validation_status: str
    warnings: list[str] = Field(default_factory=list)


class KnowledgeResult(BaseModel):
    answer: str | None = None
    documents: list[dict[str, Any]] = Field(default_factory=list)
    citations: list[Citation] = Field(default_factory=list)


class IntentAnalysis(BaseModel):
    intent: Intent
    normalized_query: str
    requires_rag: bool
    requires_business_data: bool
