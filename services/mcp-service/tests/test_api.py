from fastapi.testclient import TestClient

from app.main import app


def test_health_readiness_info_and_mcp_mount():
    with TestClient(app, base_url="http://127.0.0.1") as client:
        assert client.get("/health").json()["status"] == "healthy"
        assert client.get("/ready").json()["mcp_endpoint"] == "/mcp"
        assert client.get("/info").json()["port"] == 8005
        response = client.get("/mcp")
        assert response.status_code == 406
