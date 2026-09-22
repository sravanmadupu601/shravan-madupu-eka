import pytest
from fastapi.testclient import TestClient

from app.api.dependencies import get_orchestrator
from app.citations.domain.models import CitationBuilder
from app.context.application.assembler import DefaultContextAssembler
from app.generation.application.service import GenerationService
from app.generation.infrastructure.local_provider import DeterministicLocalProvider
from app.main import app
from app.query.application.processor import DefaultQueryProcessor
from app.rag.application.orchestrator import RAGOrchestrator
from app.retrieval.application.retriever import DefaultRetriever
from app.retrieval.domain.models import RetrievalResult
from app.retrieval.infrastructure.memory_repository import InMemoryVectorRepository, StoredVector
from app.reranking.application.pass_through import PassThroughReranker


class FakeQueryEmbeddingProvider:
    def embed_query(self, text):
        return [1.0, 0.0]

    def get_dimension(self):
        return 2

    def get_model_name(self):
        return "fake"


@pytest.fixture
def orchestrator():
    import uuid

    document_id = uuid.uuid4()
    chunk_id = uuid.uuid4()
    repository = InMemoryVectorRepository([
        StoredVector(document_id, chunk_id, "Deployment uses a reviewed local process.", [1.0, 0.0], "policy.pdf", 2)
    ])
    return RAGOrchestrator(
        DefaultQueryProcessor(), FakeQueryEmbeddingProvider(), DefaultRetriever(repository),
        PassThroughReranker(), DefaultContextAssembler(), CitationBuilder(),
        GenerationService(DeterministicLocalProvider()), 5, 0.0, 1000,
    )


@pytest.fixture
def client(orchestrator):
    app.dependency_overrides[get_orchestrator] = lambda: orchestrator
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
