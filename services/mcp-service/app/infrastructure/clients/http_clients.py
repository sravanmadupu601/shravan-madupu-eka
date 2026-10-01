from __future__ import annotations

import logging
from uuid import UUID

import httpx
from pydantic import ValidationError

from app.domain.errors import (
    DocumentNotFoundError,
    DownstreamResponseError,
    DownstreamUnavailableError,
    InvalidToolInputError,
)
from app.domain.models import DocumentPage, DocumentRecord, DownstreamHealth, KnowledgeSearchResult

logger = logging.getLogger(__name__)


class _LocalHttpClient:
    def __init__(
        self,
        base_url: str,
        timeout_seconds: float,
        transport: httpx.BaseTransport | None = None,
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds
        self.transport = transport

    def _request(self, method: str, path: str, **kwargs) -> httpx.Response:
        try:
            with httpx.Client(
                base_url=self.base_url,
                timeout=self.timeout_seconds,
                transport=self.transport,
            ) as client:
                return client.request(method, path, **kwargs)
        except httpx.TimeoutException as exc:
            raise DownstreamUnavailableError("DOWNSTREAM_TIMEOUT", "The local EKA service request timed out.") from exc
        except httpx.RequestError as exc:
            raise DownstreamUnavailableError("DOWNSTREAM_UNAVAILABLE", "The local EKA service could not be reached.") from exc

    @staticmethod
    def _health(service: str, response: httpx.Response) -> DownstreamHealth:
        try:
            body = response.json()
            status = str(body.get("status", "unknown")) if isinstance(body, dict) else "unknown"
        except ValueError:
            status = "invalid_response"
        return DownstreamHealth(
            service=service,
            available=response.is_success,
            status_code=response.status_code,
            status=status,
        )


class RagServiceHttpClient(_LocalHttpClient):
    def health(self) -> DownstreamHealth:
        try:
            response = self._request("GET", "/health/ready")
            return self._health("rag-service", response)
        except DownstreamUnavailableError:
            return DownstreamHealth(service="rag-service", available=False, status="unavailable")

    def search(self, query: str, top_k: int) -> KnowledgeSearchResult:
        normalized = " ".join(query.split())
        if not normalized:
            raise InvalidToolInputError("INVALID_QUERY", "query must contain non-whitespace text.")
        if not 1 <= top_k <= 100:
            raise InvalidToolInputError("INVALID_TOP_K", "top_k must be between 1 and 100.")
        response = self._request("POST", "/rag/query", json={"question": normalized, "top_k": top_k})
        if not response.is_success:
            raise DownstreamUnavailableError("RAG_REQUEST_FAILED", "The local RAG service rejected the search request.")
        try:
            return KnowledgeSearchResult.model_validate(response.json())
        except (ValueError, ValidationError) as exc:
            raise DownstreamResponseError("MALFORMED_RAG_RESPONSE", "The local RAG service returned an invalid response.") from exc


class DocumentServiceHttpClient(_LocalHttpClient):
    def health(self) -> DownstreamHealth:
        try:
            response = self._request("GET", "/health/ready")
            return self._health("document-service", response)
        except DownstreamUnavailableError:
            return DownstreamHealth(service="document-service", available=False, status="unavailable")

    @staticmethod
    def _validated_document_id(document_id: str) -> str:
        try:
            return str(UUID(document_id))
        except (ValueError, TypeError, AttributeError) as exc:
            raise InvalidToolInputError("INVALID_DOCUMENT_ID", "document_id must be a valid UUID.") from exc

    def get_document(self, document_id: str) -> DocumentRecord:
        safe_id = self._validated_document_id(document_id)
        response = self._request("GET", f"/documents/{safe_id}")
        if response.status_code == 404:
            raise DocumentNotFoundError("DOCUMENT_NOT_FOUND", "No document matches the supplied ID.")
        if not response.is_success:
            raise DownstreamUnavailableError("DOCUMENT_REQUEST_FAILED", "The local document service rejected the request.")
        try:
            return DocumentRecord.model_validate(response.json())
        except (ValueError, ValidationError) as exc:
            raise DownstreamResponseError("MALFORMED_DOCUMENT_RESPONSE", "The local document service returned invalid metadata.") from exc

    def list_documents(self, limit: int, offset: int) -> DocumentPage:
        if not 1 <= limit <= 100 or offset < 0:
            raise InvalidToolInputError("INVALID_PAGE", "limit must be between 1 and 100 and offset cannot be negative.")
        response = self._request("GET", "/documents", params={"limit": limit, "offset": offset})
        if not response.is_success:
            raise DownstreamUnavailableError("DOCUMENT_LIST_FAILED", "The local document service rejected the list request.")
        try:
            return DocumentPage.model_validate(response.json())
        except (ValueError, ValidationError) as exc:
            raise DownstreamResponseError("MALFORMED_DOCUMENT_LIST", "The local document service returned an invalid list response.") from exc
