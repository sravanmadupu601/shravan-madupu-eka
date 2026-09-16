import uuid
from io import BytesIO

from docx import Document as DocxDocument
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


DOCX_CONTENT_TYPE = (
    "application/vnd.openxmlformats-officedocument."
    "wordprocessingml.document"
)


def create_test_docx(content: str) -> bytes:
    buffer = BytesIO()

    document = DocxDocument()

    document.add_paragraph(content)

    document.save(buffer)

    return buffer.getvalue()


def test_document_upload():
    unique_id = uuid.uuid4()

    file_content = create_test_docx(
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

    file_content = create_test_docx(
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


def test_database_readiness():
    response = client.get("/health/ready")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ready"
    assert data["database"] == "connected"
    assert data["result"] == 1