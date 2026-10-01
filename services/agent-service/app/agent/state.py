from typing import Any, TypedDict

from app.domain.models import Citation


class AgentState(TypedDict):
    user_query: str
    normalized_query: str
    intent: str
    route: str
    requires_rag: bool
    requires_business_data: bool
    rewritten_query: str | None
    retrieved_documents: list[dict[str, Any]]
    knowledge_answer: str | None
    tool_results: dict[str, Any]
    citations: list[Citation]
    context: str
    answer: str
    retry_count: int
    max_retries: int
    validation_status: str
    errors: list[str]
    warnings: list[str]
    tools_used: list[str]
