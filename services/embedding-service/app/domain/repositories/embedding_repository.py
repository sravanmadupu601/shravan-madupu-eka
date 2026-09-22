from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.entities.embedding import Embedding


class EmbeddingRepository(ABC):
    @abstractmethod
    def get_by_key(
        self,
        document_id: UUID,
        chunk_id: UUID,
        model_name: str,
        model_version: str,
    ) -> Embedding | None:
        raise NotImplementedError

    @abstractmethod
    def list_by_document(self, document_id: UUID) -> list[Embedding]:
        raise NotImplementedError

    @abstractmethod
    def save_many(self, embeddings: list[Embedding]) -> list[Embedding]:
        raise NotImplementedError
