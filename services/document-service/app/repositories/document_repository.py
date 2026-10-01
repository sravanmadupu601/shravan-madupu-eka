import uuid

from sqlalchemy import func, select
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

    def list_documents(self, limit: int, offset: int) -> tuple[list[Document], int]:
        items_statement = (
            select(Document)
            .order_by(Document.created_at.desc(), Document.id)
            .limit(limit)
            .offset(offset)
        )
        count_statement = select(func.count()).select_from(Document)
        items = list(self.db.execute(items_statement).scalars())
        total = self.db.execute(count_statement).scalar_one()
        return items, total

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