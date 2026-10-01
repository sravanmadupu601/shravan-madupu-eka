import httpx
import pytest

from app.domain.errors import DocumentNotFoundError, DownstreamResponseError, DownstreamUnavailableError
from app.infrastructure.clients.http_clients import DocumentServiceHttpClient, RagServiceHttpClient


def test_rag_client_posts_published_contract_and_preserves_citations():
    requests = []

    def handler(request):
        requests.append(request)
        return httpx.Response(200, json={
            "answer": "Use the policy.",
            "retrieved_chunks": 1,
            "citations": [{
                "document_id": "11111111-1111-4111-8111-111111111111",
                "chunk_id": "22222222-2222-4222-8222-222222222222",
                "source": "policy.pdf",
                "page_number": 2,
                "score": 0.87,
            }],
        })

    client = RagServiceHttpClient("http://127.0.0.1:8003", 2, httpx.MockTransport(handler))
    result = client.search("cancellation policy", 4)

    assert requests[0].url.path == "/rag/query"
    assert requests[0].read() == b'{"question":"cancellation policy","top_k":4}'
    assert result.citations[0].source == "policy.pdf"


def test_document_client_fetches_and_lists_api_metadata():
    def handler(request):
        if request.url.path == "/documents":
            return httpx.Response(200, json={"documents": [], "total": 0, "limit": 10, "offset": 1})
        return httpx.Response(200, json={
            "id": "11111111-1111-4111-8111-111111111111",
            "filename": "policy.pdf",
            "content_type": "application/pdf",
            "file_size": 100,
            "checksum": "a" * 64,
            "status": "READY",
            "version": 1,
            "created_at": "2026-09-01T00:00:00Z",
            "updated_at": "2026-09-01T00:00:00Z",
        })

    client = DocumentServiceHttpClient("http://127.0.0.1:8000", 2, httpx.MockTransport(handler))
    assert client.get_document("11111111-1111-4111-8111-111111111111").filename == "policy.pdf"
    assert client.list_documents(10, 1).total == 0


def test_document_not_found_and_malformed_response():
    not_found = DocumentServiceHttpClient(
        "http://127.0.0.1:8000", 2,
        httpx.MockTransport(lambda request: httpx.Response(404)),
    )
    with pytest.raises(DocumentNotFoundError):
        not_found.get_document("11111111-1111-4111-8111-111111111111")

    malformed = RagServiceHttpClient(
        "http://127.0.0.1:8003", 2,
        httpx.MockTransport(lambda request: httpx.Response(200, json={"bad": True})),
    )
    with pytest.raises(DownstreamResponseError):
        malformed.search("question", 5)


def test_timeout_is_mapped_without_leaking_transport_details():
    def handler(request):
        raise httpx.ReadTimeout("private timeout detail")

    client = RagServiceHttpClient("http://127.0.0.1:8003", 1, httpx.MockTransport(handler))
    with pytest.raises(DownstreamUnavailableError) as exc_info:
        client.search("question", 5)
    assert "private timeout detail" not in str(exc_info.value)
