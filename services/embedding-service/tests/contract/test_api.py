import uuid


def test_health_endpoints(client):
    assert client.get("/health").json() == {"status": "healthy"}
    assert client.get("/health/live").json() == {"status": "live"}
    assert client.get("/health/ready").status_code == 200
    assert client.get("/health/db").status_code == 200


def test_create_and_get_embeddings(client):
    document_id = uuid.uuid4()
    chunk_id = uuid.uuid4()
    response = client.post(
        "/embeddings",
        json={
            "document_id": str(document_id),
            "chunks": [{"chunk_id": str(chunk_id), "text": "hello"}],
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["document_id"] == str(document_id)
    assert data["status"] == "COMPLETED"
    assert data["dimension"] == 3
    assert data["embeddings"][0]["chunk_id"] == str(chunk_id)

    retrieved = client.get(f"/embeddings/{document_id}")
    assert retrieved.status_code == 200
    assert retrieved.json()["count"] == 1


def test_duplicate_chunk_ids_are_rejected(client):
    document_id = uuid.uuid4()
    chunk_id = uuid.uuid4()
    response = client.post(
        "/embeddings",
        json={
            "document_id": str(document_id),
            "chunks": [
                {"chunk_id": str(chunk_id), "text": "one"},
                {"chunk_id": str(chunk_id), "text": "two"},
            ],
        },
    )
    assert response.status_code == 422
