import uuid

from app.application.services.embedding_service import EmbeddingApplicationService
from app.infrastructure.repositories.postgres_embedding_repository import PostgresEmbeddingRepository


class VersionedFakeProvider:
    def __init__(self, version: str):
        self.version = version

    def embed_text(self, text: str) -> list[float]:
        return self.embed_texts([text])[0]

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        return [[1.0, 2.0, 3.0] for _ in texts]

    def get_dimension(self) -> int:
        return 3

    def get_model_name(self) -> str:
        return "fake-model"

    def get_model_version(self) -> str:
        return self.version


def test_application_service_uses_provider_and_is_idempotent(db_session, provider):
    service = EmbeddingApplicationService(
        db_session,
        PostgresEmbeddingRepository(db_session),
        provider,
    )
    document_id = uuid.uuid4()
    chunk_id = uuid.uuid4()

    first = service.embed_chunks(document_id, [(chunk_id, "hello")])
    second = service.embed_chunks(document_id, [(chunk_id, "hello")])

    assert first[0].id == second[0].id
    assert first[0].dimension == 3
    assert len(service.list_document_embeddings(document_id)) == 1


def test_different_model_version_creates_new_embedding(db_session, provider):
    document_id = uuid.uuid4()
    chunk_id = uuid.uuid4()
    first_service = EmbeddingApplicationService(
        db_session,
        PostgresEmbeddingRepository(db_session),
        provider,
    )
    first_service.embed_chunks(document_id, [(chunk_id, "hello")])

    second_service = EmbeddingApplicationService(
        db_session,
        PostgresEmbeddingRepository(db_session),
        VersionedFakeProvider(version="v2"),
    )
    second_service.embed_chunks(document_id, [(chunk_id, "hello")])

    assert len(second_service.list_document_embeddings(document_id)) == 2
