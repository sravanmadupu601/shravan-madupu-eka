import os

os.environ.setdefault("DATABASE_URL", "sqlite:///./test-embedding.db")
os.environ.setdefault("EMBEDDING_MODEL_NAME", "test-model")
os.environ.setdefault("EMBEDDING_MODEL_VERSION", "test-v1")
os.environ.setdefault("EMBEDDING_DIMENSION", "3")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.dependencies import get_embedding_service
from app.application.services.embedding_service import EmbeddingApplicationService
from app.db import Base
from app.domain.providers.embedding_provider import EmbeddingProvider
from app.infrastructure.repositories.postgres_embedding_repository import PostgresEmbeddingRepository
from app.main import app


class FakeEmbeddingProvider(EmbeddingProvider):
    def __init__(self, dimension: int = 3, name: str = "fake-model", version: str = "v1"):
        self.dimension = dimension
        self.name = name
        self.version = version

    def embed_text(self, text: str) -> list[float]:
        return self.embed_texts([text])[0]

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        return [[float(index + 1) for index in range(self.dimension)] for _ in texts]

    def get_dimension(self) -> int:
        return self.dimension

    def get_model_name(self) -> str:
        return self.name

    def get_model_version(self) -> str:
        return self.version


@pytest.fixture(scope="session")
def engine():
    test_engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(test_engine)
    yield test_engine
    Base.metadata.drop_all(test_engine)
    test_engine.dispose()


@pytest.fixture
def db_session(engine):
    factory = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    session = factory()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture
def provider():
    return FakeEmbeddingProvider()


@pytest.fixture
def client(db_session, provider):
    def override_service():
        return EmbeddingApplicationService(
            db_session,
            PostgresEmbeddingRepository(db_session),
            provider,
        )

    app.dependency_overrides[get_embedding_service] = override_service
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
