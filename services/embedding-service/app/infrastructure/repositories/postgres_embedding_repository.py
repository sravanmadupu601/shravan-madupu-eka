from uuid import UUID
import math

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.entities.embedding import Embedding, EmbeddingSearchResult
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

    def search_similar(
        self,
        query_embedding: list[float],
        top_k: int,
        similarity_threshold: float | None = None,
        filters: dict[str, str] | None = None,
    ) -> list[EmbeddingSearchResult]:
        if top_k <= 0:
            raise ValueError("top_k must be greater than zero.")
        filters = filters or {}
        if self.db.bind is not None and self.db.bind.dialect.name != "postgresql":
            return self._search_similar_for_test_backend(
                query_embedding,
                top_k,
                similarity_threshold,
                filters,
            )
        distance = EmbeddingModel.embedding.cosine_distance(query_embedding).label("distance")
        statement = select(EmbeddingModel, distance)
        if filters.get("document_id"):
            statement = statement.where(EmbeddingModel.document_id == filters["document_id"])
        if filters.get("model_name"):
            statement = statement.where(EmbeddingModel.model_name == filters["model_name"])
        if filters.get("model_version"):
            statement = statement.where(EmbeddingModel.model_version == filters["model_version"])
        statement = statement.order_by(distance).limit(top_k)
        results = []
        for model, value in self.db.execute(statement):
            numeric_distance = float(value)
            similarity = 1.0 - numeric_distance
            if similarity_threshold is not None and similarity < similarity_threshold:
                continue
            results.append(
                EmbeddingSearchResult(
                    embedding=self._to_entity(model),
                    distance=numeric_distance,
                    similarity=similarity,
                )
            )
        return results

    def _search_similar_for_test_backend(
        self,
        query_embedding: list[float],
        top_k: int,
        similarity_threshold: float | None,
        filters: dict[str, str],
    ) -> list[EmbeddingSearchResult]:
        query_norm = math.sqrt(sum(value * value for value in query_embedding))
        if query_norm == 0:
            return []
        statement = select(EmbeddingModel)
        if filters.get("document_id"):
            statement = statement.where(EmbeddingModel.document_id == filters["document_id"])
        if filters.get("model_name"):
            statement = statement.where(EmbeddingModel.model_name == filters["model_name"])
        if filters.get("model_version"):
            statement = statement.where(EmbeddingModel.model_version == filters["model_version"])
        results = []
        for model in self.db.execute(statement).scalars():
            vector = list(model.embedding)
            if len(vector) != len(query_embedding):
                continue
            vector_norm = math.sqrt(sum(value * value for value in vector))
            similarity = (
                sum(a * b for a, b in zip(vector, query_embedding)) / (query_norm * vector_norm)
                if vector_norm
                else 0.0
            )
            if similarity_threshold is None or similarity >= similarity_threshold:
                results.append(
                    EmbeddingSearchResult(
                        embedding=self._to_entity(model),
                        distance=1.0 - similarity,
                        similarity=similarity,
                    )
                )
        return sorted(results, key=lambda result: result.distance)[:top_k]

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
