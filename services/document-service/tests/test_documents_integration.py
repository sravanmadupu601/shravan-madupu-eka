import uuid

from fastapi.testclient import TestClient

from app.main import app
from app.core.config import settings


client = TestClient(app)


DOCX_CONTENT_TYPE = (
    "application/vnd.openxmlformats-officedocument."
    "wordprocessingml.document"
)


def create_test_file(content: str) -> bytes:
    return content.encode("utf-8")


def test_document_upload():
    unique_id = uuid.uuid4()

    file_content = create_test_file(
        f"EKA integration test document {unique_id}"
    )

    response = client.post(
        "/documents/upload",
        files={
            "file": (
                f"integration-test-{unique_id}.docx",
                file_content,
                DOCX_CONTENT_TYPE,
            )
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "READY"
    assert data["version"] == 1
    assert data["file_size"] > 0
    assert data["checksum"]


def test_duplicate_document_upload():
    unique_id = uuid.uuid4()

    file_content = create_test_file(
        f"EKA duplicate detection test {unique_id}"
    )

    first_response = client.post(
        "/documents/upload",
        files={
            "file": (
                f"duplicate-test-{unique_id}.docx",
                file_content,
                DOCX_CONTENT_TYPE,
            )
        },
    )

    assert first_response.status_code == 200

    second_response = client.post(
        "/documents/upload",
        files={
            "file": (
                f"duplicate-test-{unique_id}.docx",
                file_content,
                DOCX_CONTENT_TYPE,
            )
        },
    )

    assert second_response.status_code == 409

    assert (
        second_response.json()["detail"]
        == "A document with this content already exists."
    )


def test_document_upload_rejects_oversized_file():
    file_content = b"x" * (settings.max_file_size_mb * 1024 * 1024 + 1)

    response = client.post(
        "/documents/upload",
        files={
            "file": (
                "oversized-document.pdf",
                file_content,
                "application/pdf",
            )
        },
    )

    assert response.status_code == 413
    assert response.json()["detail"] == (
        f"File size exceeds the maximum allowed size of "
        f"{settings.max_file_size_mb} MB."
    )


def test_database_readiness():
    response = client.get("/health/ready")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ready"
    assert data["database"] == "connected"
    assert data["result"] == 1