import pytest

from app.application.service import MCPApplicationService
from app.domain.models import DocumentPage, DocumentRecord, DownstreamHealth, KnowledgeSearchResult


class FakeRagClient:
    def __init__(self, result=None, error=None):
        self.result = result or KnowledgeSearchResult(answer="Policy result", citations=[], retrieved_chunks=0)
        self.error = error
        self.queries = []

    def search(self, query, top_k):
        self.queries.append((query, top_k))
        if self.error:
            raise self.error
        return self.result

    def health(self):
        return DownstreamHealth(service="rag-service", available=True, status_code=200, status="ready")


class FakeDocumentClient:
    def __init__(self, document=None, page=None, error=None):
        self.document = document or DocumentRecord(
            id="11111111-1111-4111-8111-111111111111",
            filename="policy.pdf",
            content_type="application/pdf",
            file_size=120,
            checksum="a" * 64,
            status="READY",
            version=1,
            created_at="2026-09-01T00:00:00Z",
            updated_at="2026-09-01T00:00:00Z",
        )
        self.page = page or DocumentPage(documents=[self.document], total=1, limit=5, offset=0)
        self.error = error
        self.document_ids = []
        self.pages = []

    def get_document(self, document_id):
        self.document_ids.append(document_id)
        if self.error:
            raise self.error
        return self.document

    def list_documents(self, limit, offset):
        self.pages.append((limit, offset))
        if self.error:
            raise self.error
        return self.page.model_copy(update={"limit": limit, "offset": offset})

    def health(self):
        return DownstreamHealth(service="document-service", available=True, status_code=200, status="ready")


@pytest.fixture
def clients():
    return FakeRagClient(), FakeDocumentClient()


@pytest.fixture
def application_service(clients):
    rag_client, document_client = clients
    return MCPApplicationService(rag_client, document_client, max_document_page_size=100)
