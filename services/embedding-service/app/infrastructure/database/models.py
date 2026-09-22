import uuid
from datetime import datetime

from sqlalchemy import DateTime, JSON, Integer, String, UniqueConstraint, Uuid, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from app.config.settings import settings

try:
    from pgvector.sqlalchemy import Vector
except ImportError:
    Vector = None


class Base(DeclarativeBase):
    pass


class EmbeddingModel(Base):
    __tablename__ = "embeddings"
    __table_args__ = (
        UniqueConstraint(
            "document_id",
            "chunk_id",
            "model_name",
            "model_version",
            name="uq_embedding_chunk_model_version",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), nullable=False, index=True)
    chunk_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), nullable=False, index=True)
    embedding: Mapped[list[float]] = mapped_column(
        (Vector(settings.configured_vector_dimension) if Vector is not None else JSON),
        nullable=False,
    )
    model_name: Mapped[str] = mapped_column(String(255), nullable=False)
    model_version: Mapped[str] = mapped_column(String(100), nullable=False)
    embedding_dimension: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
