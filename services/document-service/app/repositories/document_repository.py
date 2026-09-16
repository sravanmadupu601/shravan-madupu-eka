import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.document import Document


class DocumentRepository:
    """Handles database operations for documents."""

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        document: Document,
    ) -> Document:
        self.db.add(document)
        self.db.flush()

        return document

    def get_by_id(
        self,
        document_id: uuid.UUID,
    ) -> Document | None:
        statement = select(Document).where(
            Document.id == document_id
        )

        return self.db.execute(
            statement
        ).scalar_one_or_none()

    def get_by_checksum(
        self,
        checksum: str,
    ) -> Document | None:
        statement = select(Document).where(
            Document.checksum == checksum
        )

        return self.db.execute(
            statement
        ).scalar_one_or_none()

    def delete(
        self,
        document: Document,
    ) -> None:
        self.db.delete(document)