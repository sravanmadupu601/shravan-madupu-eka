from functools import lru_cache

from app.application.service import MCPApplicationService
from app.config.settings import settings
from app.infrastructure.clients.http_clients import DocumentServiceHttpClient, RagServiceHttpClient


@lru_cache(maxsize=1)
def get_mcp_application_service() -> MCPApplicationService:
    rag_client = RagServiceHttpClient(settings.rag_service_url, settings.request_timeout_seconds)
    document_client = DocumentServiceHttpClient(settings.document_service_url, settings.request_timeout_seconds)
    return MCPApplicationService(rag_client, document_client, settings.max_document_page_size)
