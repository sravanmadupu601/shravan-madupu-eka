from typing import Any, Protocol

from app.domain.models import Citation, KnowledgeResult


class RagClient(Protocol):
    def search_knowledge(self, query: str) -> KnowledgeResult: ...


class DocumentClient(Protocol):
    def get_document(self, document_id: str) -> dict[str, Any] | None: ...


class BusinessDataClient(Protocol):
    def get_reservation(self, reservation_id: str) -> dict[str, Any] | None: ...


class LLMProvider(Protocol):
    def generate(
        self,
        *,
        query: str,
        intent: str,
        knowledge: KnowledgeResult | None,
        business_data: dict[str, Any] | None,
        warnings: list[str],
    ) -> str: ...


class AgentRunner(Protocol):
    def invoke(
        self,
        state: dict[str, Any],
        config: dict[str, Any] | None = None,
    ) -> dict[str, Any]: ...
