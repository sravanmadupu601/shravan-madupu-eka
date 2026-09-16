from uuid import UUID

from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.db.models.document_chunk import DocumentChunk


class ChunkRepository:
    """Handles database operations for document chunks."""

    def __init__(self, db: Session):
        self.db = db

    def create_many(
        self,
        chunks: list[DocumentChunk],
    ) -> None:
        self.db.add_all(chunks)
        self.db.flush()

    def delete_by_document_id(
        self,
        document_id: UUID,
    ) -> None:
        statement = delete(DocumentChunk).where(
            DocumentChunk.document_id == document_id
        )

        self.db.execute(statement)
        self.db.flush()