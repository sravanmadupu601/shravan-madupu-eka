from collections.abc import Generator

from fastapi import Depends
from sqlalchemy.orm import Session

from app.config.settings import settings
from app.infrastructure.database.session import get_db
from app.infrastructure.embeddings.sentence_transformer_provider import SentenceTransformerEmbeddingProvider
from app.infrastructure.repositories.postgres_embedding_repository import PostgresEmbeddingRepository


def get_embedding_provider() -> SentenceTransformerEmbeddingProvider:
    return SentenceTransformerEmbeddingProvider(
        model_name=settings.embedding_model_name,
        model_version=settings.embedding_model_version,
        dimension=settings.embedding_dimension,
    )


def get_embedding_service(
    db: Session = Depends(get_db),
    provider=Depends(get_embedding_provider),
):
    from app.application.services.embedding_service import EmbeddingApplicationService

    return EmbeddingApplicationService(db, PostgresEmbeddingRepository(db), provider)


def get_database() -> Generator[Session, None, None]:
    yield from get_db()
