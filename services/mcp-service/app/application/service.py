from __future__ import annotations

import json
import logging
from time import perf_counter
from typing import Any, Callable

from app.domain.errors import InvalidToolInputError, MCPServiceError
from app.domain.interfaces import DocumentServiceClient, RagServiceClient

logger = logging.getLogger(__name__)


class MCPApplicationService:
    def __init__(
        self,
        rag_client: RagServiceClient,
        document_client: DocumentServiceClient,
        max_document_page_size: int = 100,
    ):
        self.rag_client = rag_client
        self.document_client = document_client
        self.max_document_page_size = max_document_page_size

    def _invoke(self, tool_name: str, operation: Callable[[], Any]) -> dict[str, Any]:
        started = perf_counter()
        try:
            data = operation()
            result = data.model_dump(mode="json") if hasattr(data, "model_dump") else data
            logger.info("MCP tool completed: name=%s success=true duration_ms=%.2f", tool_name, (perf_counter() - started) * 1000)
            return {"ok": True, "data": result}
        except MCPServiceError as exc:
            logger.warning("MCP tool failed: name=%s code=%s duration_ms=%.2f", tool_name, exc.code, (perf_counter() - started) * 1000)
            return {"ok": False, "error": {"code": exc.code, "message": exc.message}}
        except Exception:
            logger.error("MCP tool failed unexpectedly: name=%s duration_ms=%.2f", tool_name, (perf_counter() - started) * 1000)
            return {"ok": False, "error": {"code": "INTERNAL_ERROR", "message": "The tool could not complete the request."}}

    @staticmethod
    def _reject_input(code: str, message: str) -> None:
        raise InvalidToolInputError(code, message)

    def search_knowledge(self, query: str, top_k: int = 5) -> dict[str, Any]:
        if not query.strip():
            return self._invoke(
                "search_knowledge",
                lambda: self._reject_input("INVALID_QUERY", "query must contain non-whitespace text."),
            )
        if not 1 <= top_k <= 100:
            return self._invoke(
                "search_knowledge",
                lambda: self._reject_input("INVALID_TOP_K", "top_k must be between 1 and 100."),
            )
        return self._invoke("search_knowledge", lambda: self.rag_client.search(query, top_k))

    def get_document(self, document_id: str) -> dict[str, Any]:
        return self._invoke("get_document", lambda: self.document_client.get_document(document_id))

    def list_documents(self, limit: int = 50, offset: int = 0) -> dict[str, Any]:
        if not 1 <= limit <= min(100, self.max_document_page_size) or offset < 0:
            return self._invoke(
                "list_documents",
                lambda: self._reject_input(
                    "INVALID_PAGE",
                    f"limit must be between 1 and {min(100, self.max_document_page_size)} and offset cannot be negative.",
                ),
            )
        bounded_limit = min(limit, self.max_document_page_size)
        return self._invoke("list_documents", lambda: self.document_client.list_documents(bounded_limit, offset))

    def document_health(self) -> dict[str, Any]:
        return self._invoke("document_health", self.document_client.health)

    def rag_health(self) -> dict[str, Any]:
        return self._invoke("rag_health", self.rag_client.health)

    def documents_resource(self) -> str:
        return json.dumps(self.list_documents(limit=min(50, self.max_document_page_size), offset=0), ensure_ascii=True)
