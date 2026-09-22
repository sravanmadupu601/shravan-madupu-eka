import logging
from time import perf_counter
from uuid import UUID, uuid4

from sqlalchemy.orm import Session

from app.domain.entities.embedding import Embedding
from app.domain.exceptions import EmbeddingDimensionError
from app.domain.providers.embedding_provider import EmbeddingProvider
from app.domain.repositories.embedding_repository import EmbeddingRepository

logger = logging.getLogger(__name__)


class EmbeddingApplicationService:
    def __init__(
        self,
        db: Session,
        repository: EmbeddingRepository,
        provider: EmbeddingProvider,
    ):
        self.db = db
        self.repository = repository
        self.provider = provider

    def embed_chunks(self, document_id: UUID, chunks: list[tuple[UUID, str]]) -> list[Embedding]:
        started = perf_counter()
        model_name = self.provider.get_model_name()
        model_version = self.provider.get_model_version()
        pending: list[tuple[UUID, str]] = []
        results_by_chunk: dict[UUID, Embedding] = {}

        for chunk_id, text in chunks:
            existing = self.repository.get_by_key(
                document_id,
                chunk_id,
                model_name,
                model_version,
            )
            if existing:
                results_by_chunk[chunk_id] = existing
            else:
                pending.append((chunk_id, text))

        try:
            if pending:
                vectors = self.provider.embed_texts([text for _, text in pending])
                if len(vectors) != len(pending):
                    raise EmbeddingDimensionError("Embedding provider returned an unexpected result count.")
                expected_dimension = self.provider.get_dimension()
                if any(len(vector) != expected_dimension for vector in vectors):
                    raise EmbeddingDimensionError("Embedding provider returned an unexpected dimension.")
                new_embeddings = [
                    Embedding(
                        id=uuid4(),
                        document_id=document_id,
                        chunk_id=chunk_id,
                        vector=vector,
                        model_name=model_name,
                        model_version=model_version,
                        dimension=expected_dimension,
                    )
                    for (chunk_id, _), vector in zip(pending, vectors, strict=True)
                ]
                for embedding in self.repository.save_many(new_embeddings):
                    results_by_chunk[embedding.chunk_id] = embedding
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise

        logger.info(
            "Embedding processing completed: document_id=%s model=%s version=%s chunks=%d duration_ms=%.2f",
            document_id,
            model_name,
            model_version,
            len(chunks),
            (perf_counter() - started) * 1000,
        )
        return [results_by_chunk[chunk_id] for chunk_id, _ in chunks]

    def list_document_embeddings(self, document_id: UUID) -> list[Embedding]:
        return self.repository.list_by_document(document_id)
