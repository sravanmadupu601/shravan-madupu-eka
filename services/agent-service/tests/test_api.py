import pytest
from pydantic import ValidationError

from app.config.settings import Settings


def test_agent_query_api(api_client):
    response = api_client.post("/agent/query", json={"query": "Hello"})
    assert response.status_code == 200
    assert response.json()["intent"] == "GENERAL"
    assert response.json()["tools_used"] == []


def test_agent_query_validates_request(api_client):
    assert api_client.post("/agent/query", json={"query": " "}).status_code == 422
    assert api_client.post("/agent/query", json={}).status_code == 422


def test_health_readiness_and_info(api_client):
    assert api_client.get("/health").json() == {"status": "healthy"}
    ready = api_client.get("/ready")
    assert ready.status_code == 200
    assert ready.json()["rag_integration"] in {"available", "unavailable"}
    info = api_client.get("/info").json()
    assert info["port"] == 8004
    assert "validate_results" in info["graph_nodes"]


def test_settings_reject_remote_service_urls():
    with pytest.raises(ValidationError):
        Settings(rag_service_url="https://example.com")
