import json
import uuid

import httpx

from app.retrieval.domain.models import RetrievalRequest
from app.retrieval.infrastructure.pgvector_repository import PgVectorRepository


def test_pgvector_repository_delegates_search_and_resolves_chunk_content():
    document_id = str(uuid.uuid4())
    chunk_id = str(uuid.uuid4())
    requests = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        if request.url.path == "/embeddings/search":
            return httpx.Response(
                200,
                json=[
                    {
                        "document_id": document_id,
                        "chunk_id": chunk_id,
                        "similarity": 0.91,
                        "distance": 0.09,
                    }
                ],
            )
        assert request.url.path == "/ingestion/chunks/lookup"
        assert json.loads(request.content)["chunk_ids"] == [chunk_id]
        return httpx.Response(
            200,
            json={
                "chunks": [
                    {
                        "document_id": document_id,
                        "chunk_id": chunk_id,
                        "text": "Cancel at least five days before check-in.",
                        "source": "policy.pdf",
                        "page_number": 2,
                        "metadata": {"chunking_strategy": "fixed"},
                    }
                ]
            },
        )

    repository = PgVectorRepository(
        "http://127.0.0.1:8002",
        "http://127.0.0.1:8001",
        transport=httpx.MockTransport(handler),
    )
    results = repository.search(
        RetrievalRequest([0.1, 0.2], top_k=3, similarity_threshold=0.5)
    )

    assert len(requests) == 2
    assert json.loads(requests[0].content)["top_k"] == 3
    assert results[0].text == "Cancel at least five days before check-in."
    assert results[0].source == "policy.pdf"
    assert results[0].score == 0.91


def test_pgvector_repository_drops_hits_without_matching_ingestion_chunk():
    document_id = str(uuid.uuid4())
    chunk_id = str(uuid.uuid4())

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/embeddings/search":
            return httpx.Response(
                200,
                json=[{"document_id": document_id, "chunk_id": chunk_id, "similarity": 0.8}],
            )
        return httpx.Response(200, json={"chunks": []})

    repository = PgVectorRepository(
        "http://127.0.0.1:8002",
        "http://127.0.0.1:8001",
        transport=httpx.MockTransport(handler),
    )
    assert repository.search(RetrievalRequest([1.0], top_k=1)) == []
