import uuid

from app.application.services.embedding_service import EmbeddingApplicationService
from app.infrastructure.repositories.postgres_embedding_repository import PostgresEmbeddingRepository


def test_similarity_search_orders_top_k_and_applies_threshold(db_session, provider):
    service = EmbeddingApplicationService(db_session, PostgresEmbeddingRepository(db_session), provider)
    document_id = uuid.uuid4()
    service.embed_chunks(
        document_id,
        [(uuid.uuid4(), "first"), (uuid.uuid4(), "second")],
    )

    results = service.search_similar([1.0, 2.0, 3.0], top_k=1, similarity_threshold=0.99)

    assert len(results) == 1
    assert results[0].similarity == 1.0
    assert results[0].distance == 0.0


def test_similarity_search_filters_by_document(db_session, provider):
    service = EmbeddingApplicationService(db_session, PostgresEmbeddingRepository(db_session), provider)
    matching_document_id = uuid.uuid4()
    other_document_id = uuid.uuid4()
    service.embed_chunks(matching_document_id, [(uuid.uuid4(), "matching")])
    service.embed_chunks(other_document_id, [(uuid.uuid4(), "other")])

    results = service.search_similar(
        [1.0, 2.0, 3.0],
        top_k=5,
        filters={"document_id": str(matching_document_id)},
    )

    assert len(results) == 1
    assert results[0].embedding.document_id == matching_document_id