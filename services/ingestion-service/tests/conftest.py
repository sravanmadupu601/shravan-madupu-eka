import os
from pathlib import Path

os.environ.setdefault("DATABASE_URL", "sqlite:///./test-ingestion.db")
os.environ.setdefault("DOCUMENT_STORAGE_PATH", "./test-storage")
os.environ.setdefault("CHUNK_SIZE", "100")
os.environ.setdefault("CHUNK_OVERLAP", "20")
os.environ.setdefault("PROCESSING_VERSION", "1.0")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.db.database import Base, get_db
from app.main import app


@pytest.fixture(scope="session")
def engine():
    test_engine = create_engine("sqlite:///./test-ingestion.db")
    Base.metadata.create_all(test_engine)
    yield test_engine
    Base.metadata.drop_all(test_engine)
    test_engine.dispose()
    Path("test-ingestion.db").unlink(missing_ok=True)


@pytest.fixture
def db_session(engine):
    session_factory = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    session = session_factory()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture
def client(db_session, tmp_path, monkeypatch):
    from app.core.config import settings

    monkeypatch.setattr(settings, "document_storage_path", str(tmp_path))

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
