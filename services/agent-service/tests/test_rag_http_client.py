import json

import httpx

from app.tools.rag_tool import HttpRagClient


def test_rag_http_adapter_uses_published_request_and_maps_citations():
    requests = []

    def handle(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(
            200,
            json={
                "answer": "Policy answer from Block 4.",
                "retrieved_chunks": 1,
                "citations": [
                    {
                        "document_id": "doc-1",
                        "chunk_id": "chunk-1",
                        "source": "policy.pdf",
                        "page_number": 3,
                        "score": 0.91,
                    }
                ],
            },
        )

    rag = HttpRagClient("http://127.0.0.1:8003", transport=httpx.MockTransport(handle))
    result = rag.search_knowledge("What is the cancellation policy?")

    assert requests[0].url.path == "/rag/query"
    assert json.loads(requests[0].content) == {"question": "What is the cancellation policy?"}
    assert result.answer == "Policy answer from Block 4."
    assert result.citations[0].source == "policy.pdf"
    assert result.citations[0].page_number == 3
    assert result.citations[0].chunk_id == "chunk-1"


def test_rag_readiness_uses_health_ready_route():
    requests = []

    def handle(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200, json={"status": "ready"})

    rag = HttpRagClient("http://127.0.0.1:8003", transport=httpx.MockTransport(handle))
    assert rag.is_ready()
    assert requests[0].url.path == "/health/ready"
