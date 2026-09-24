from collections.abc import Callable

import pytest
from fastapi.testclient import TestClient

from app.api.dependencies import get_agent_service
from app.domain.models import Citation, KnowledgeResult
from app.main import app


class StubRagClient:
    def __init__(self, results=None, error: Exception | None = None):
        self.results = list(results or [])
        self.error = error
        self.queries: list[str] = []

    def search_knowledge(self, query: str) -> KnowledgeResult:
        self.queries.append(query)
        if self.error:
            raise self.error
        if self.results:
            result = self.results.pop(0)
            return result
        return KnowledgeResult()


class StubBusinessDataClient:
    def __init__(self, result=None, error: Exception | None = None):
        self.result = result
        self.error = error
        self.lookups: list[str] = []

    def get_reservation(self, reservation_id: str):
        self.lookups.append(reservation_id)
        if self.error:
            raise self.error
        return self.result


class StubLLMProvider:
    def __init__(self, error: Exception | None = None):
        self.error = error
        self.calls = 0

    def generate(self, **kwargs) -> str:
        self.calls += 1
        if self.error:
            raise self.error
        return "Generated from supplied tool results."


@pytest.fixture
def knowledge_result() -> KnowledgeResult:
    return KnowledgeResult(
        answer="Cancellation requests must meet the stated deadline.",
        documents=[{"text": "The cancellation deadline is listed in the policy."}],
        citations=[Citation(source="employee-policy.pdf", text="Cancellation deadline")],
    )


@pytest.fixture
def reservation() -> dict:
    return {
        "reservation_id": "ABC123",
        "status": "confirmed",
        "cancellation_deadline": "2026-10-10",
        "cancellation_penalty": 0,
        "data_source": "LOCAL MOCK DATA",
    }


@pytest.fixture
def api_client():
    service = get_agent_service()
    app.dependency_overrides[get_agent_service] = lambda: service
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()
