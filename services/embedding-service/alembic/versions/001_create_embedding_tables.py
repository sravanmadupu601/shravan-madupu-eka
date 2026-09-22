"""create embedding tables

Revision ID: 001
Revises:
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "001"
down_revision: Union[str, Sequence[str], None] = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "embeddings",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("document_id", sa.Uuid(), nullable=False),
        sa.Column("chunk_id", sa.Uuid(), nullable=False),
        sa.Column("embedding", sa.JSON(), nullable=False),
        sa.Column("model_name", sa.String(length=255), nullable=False),
        sa.Column("model_version", sa.String(length=100), nullable=False),
        sa.Column("embedding_dimension", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "document_id",
            "chunk_id",
            "model_name",
            "model_version",
            name="uq_embedding_chunk_model_version",
        ),
    )
    op.create_index("ix_embeddings_document_id", "embeddings", ["document_id"])
    op.create_index("ix_embeddings_chunk_id", "embeddings", ["chunk_id"])


def downgrade() -> None:
    op.drop_index("ix_embeddings_chunk_id", table_name="embeddings")
    op.drop_index("ix_embeddings_document_id", table_name="embeddings")
    op.drop_table("embeddings")
