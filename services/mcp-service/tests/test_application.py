import json

from app.application.prompts import enterprise_knowledge_query
from app.domain.errors import DocumentNotFoundError
from app.domain.models import KnowledgeSearchResult


def test_search_knowledge_returns_structured_citations(application_service, clients):
    rag, _ = clients
    rag.result = KnowledgeSearchResult(
        answer="Policy text",
        citations=[{"document_id": "doc-1", "chunk_id": "chunk-1", "source": "guide.pdf", "score": 0.9}],
        retrieved_chunks=1,
    )

    result = application_service.search_knowledge(" policy ", top_k=3)

    assert result["ok"] is True
    assert result["data"]["citations"][0]["chunk_id"] == "chunk-1"
    assert rag.queries == [(" policy ", 3)]


def test_invalid_search_input_returns_structured_error(application_service):
    result = application_service.search_knowledge("   ", 5)
    assert result["ok"] is False
    assert result["error"]["code"] == "INVALID_QUERY"


def test_document_tools_and_resource_use_client(application_service, clients):
    _, documents = clients
    document = application_service.get_document("11111111-1111-4111-8111-111111111111")
    page = application_service.list_documents(limit=100, offset=2)
    resource = json.loads(application_service.documents_resource())

    assert document["ok"] is True
    assert document["data"]["filename"] == "policy.pdf"
    assert page["ok"] is True
    assert documents.pages[0] == (100, 2)
    assert resource["ok"] is True
    assert "storage_path" not in resource["data"]["documents"][0]


def test_document_not_found_is_mapped_to_error(application_service, clients):
    _, documents = clients
    documents.error = DocumentNotFoundError("DOCUMENT_NOT_FOUND", "No document matches the supplied ID.")

    result = application_service.get_document("11111111-1111-4111-8111-111111111111")

    assert result["error"]["code"] == "DOCUMENT_NOT_FOUND"


def test_health_tools_report_local_services(application_service):
    assert application_service.document_health()["data"]["available"] is True
    assert application_service.rag_health()["data"]["available"] is True


def test_enterprise_prompt_requires_grounding_and_citations():
    prompt = enterprise_knowledge_query("policy?", "formal", True)
    assert "never invent citations" in prompt
    assert "clearly say so" in prompt
    assert "formal response style" in prompt
