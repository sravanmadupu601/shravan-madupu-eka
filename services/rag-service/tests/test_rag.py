def test_health_and_info(client):
    assert client.get("/health").json() == {"status": "healthy"}
    assert client.get("/info").json()["block"] == 4


def test_end_to_end_query(client):
    response = client.post("/rag/query", json={"question": "What is the deployment process?", "top_k": 5})

    assert response.status_code == 200
    data = response.json()
    assert data["retrieved_chunks"] == 1
    assert data["citations"][0]["source"] == "policy.pdf"
    assert "Local generation" in data["answer"]


def test_empty_query_is_rejected(client):
    response = client.post("/rag/query", json={"question": " "})
    assert response.status_code == 422
