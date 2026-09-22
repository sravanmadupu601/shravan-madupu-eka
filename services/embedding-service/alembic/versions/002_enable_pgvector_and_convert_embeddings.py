"""enable pgvector and convert existing JSON embeddings

Revision ID: 002
Revises: 001
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "002"
down_revision: Union[str, Sequence[str], None] = "001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1
                FROM embeddings
                WHERE jsonb_typeof(embedding::jsonb) <> 'array'
                   OR jsonb_array_length(embedding::jsonb) <> 384
            ) THEN
                RAISE EXCEPTION 'Existing embeddings must be JSON arrays with exactly 384 values';
            END IF;
        END $$;
        """
    )
    op.add_column("embeddings", sa.Column("embedding_vector", sa.Text(), nullable=True))
    op.execute(
        """
        UPDATE embeddings
        SET embedding_vector = (
            SELECT '[' || string_agg(value, ',' ORDER BY ordinality) || ']'
            FROM jsonb_array_elements_text(embeddings.embedding::jsonb)
            WITH ORDINALITY AS values(value, ordinality)
        )
        WHERE embedding IS NOT NULL
        """
    )
    op.alter_column("embeddings", "embedding_vector", nullable=False)
    op.execute("ALTER TABLE embeddings ALTER COLUMN embedding_vector TYPE vector(384) USING embedding_vector::vector")
    op.drop_column("embeddings", "embedding")
    op.alter_column("embeddings", "embedding_vector", new_column_name="embedding")
    op.create_index(
        "ix_embeddings_embedding_hnsw_cosine",
        "embeddings",
        ["embedding"],
        postgresql_using="hnsw",
        postgresql_ops={"embedding": "vector_cosine_ops"},
    )


def downgrade() -> None:
    op.drop_index("ix_embeddings_embedding_hnsw_cosine", table_name="embeddings")
    op.add_column("embeddings", sa.Column("embedding_json", sa.JSON(), nullable=True))
    op.execute("UPDATE embeddings SET embedding_json = embedding::text::json")
    op.alter_column("embeddings", "embedding_json", nullable=False)
    op.drop_column("embeddings", "embedding")
    op.alter_column("embeddings", "embedding_json", new_column_name="embedding")