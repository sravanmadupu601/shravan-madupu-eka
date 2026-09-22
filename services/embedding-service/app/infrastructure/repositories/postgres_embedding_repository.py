from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.entities.embedding import Embedding
from app.domain.repositories.embedding_repository import EmbeddingRepository
from app.infrastructure.database.models import EmbeddingModel


class PostgresEmbeddingRepository(EmbeddingRepository):
    def __init__(self, db: Session):
        self.db = db

    def get_by_key(
        self,
        document_id: UUID,
        chunk_id: UUID,
        model_name: str,
        model_version: str,
    ) -> Embedding | None:
        statement = select(EmbeddingModel).where(
            EmbeddingModel.document_id == document_id,
            EmbeddingModel.chunk_id == chunk_id,
            EmbeddingModel.model_name == model_name,
            EmbeddingModel.model_version == model_version,
        )
        model = self.db.execute(statement).scalar_one_or_none()
        return self._to_entity(model) if model else None

    def list_by_document(self, document_id: UUID) -> list[Embedding]:
        statement = select(EmbeddingModel).where(
            EmbeddingModel.document_id == document_id,
        ).order_by(EmbeddingModel.created_at, EmbeddingModel.chunk_id)
        return [self._to_entity(model) for model in self.db.execute(statement).scalars()]

    def save_many(self, embeddings: list[Embedding]) -> list[Embedding]:
        models = [self._to_model(embedding) for embedding in embeddings]
        self.db.add_all(models)
        self.db.flush()
        return [self._to_entity(model) for model in models]

    @staticmethod
    def _to_entity(model: EmbeddingModel) -> Embedding:
        return Embedding(
            id=model.id,
            document_id=model.document_id,
            chunk_id=model.chunk_id,
            vector=list(model.embedding),
            model_name=model.model_name,
            model_version=model.model_version,
            dimension=model.embedding_dimension,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def _to_model(embedding: Embedding) -> EmbeddingModel:
        return EmbeddingModel(
            id=embedding.id,
            document_id=embedding.document_id,
            chunk_id=embedding.chunk_id,
            embedding=embedding.vector,
            model_name=embedding.model_name,
            model_version=embedding.model_version,
            embedding_dimension=embedding.dimension,
        )
