import uuid

from sqlalchemy.exc import IntegrityError

from app.application.services.embedding_service import EmbeddingApplicationService
from app.infrastructure.repositories.postgres_embedding_repository import PostgresEmbeddingRepository


def test_repository_persists_and_retrieves_embeddings(db_session, provider):
    document_id = uuid.uuid4()
    chunk_id = uuid.uuid4()
    service = EmbeddingApplicationService(db_session, PostgresEmbeddingRepository(db_session), provider)

    saved = service.embed_chunks(document_id, [(chunk_id, "persist me")])[0]
    loaded = service.list_document_embeddings(document_id)[0]

    assert loaded.id == saved.id
    assert loaded.document_id == document_id
    assert loaded.chunk_id == chunk_id
    assert loaded.vector == [1.0, 2.0, 3.0]


def test_unique_constraint_rejects_duplicate_database_rows(db_session, provider):
    document_id = uuid.uuid4()
    chunk_id = uuid.uuid4()
    service = EmbeddingApplicationService(db_session, PostgresEmbeddingRepository(db_session), provider)
    service.embed_chunks(document_id, [(chunk_id, "once")])

    duplicate = service.repository.get_by_key(document_id, chunk_id, "fake-model", "v1")
    assert duplicate is not None
    assert len(service.list_document_embeddings(document_id)) == 1
