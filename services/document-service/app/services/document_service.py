import hashlib
import hashlib
import logging

logger = logging.getLogger(__name__)

from sqlalchemy.orm import Session
from app.core.config import settings

from app.db.models.document import Document
from app.repositories.document_repository import DocumentRepository
from app.services.storage_service import LocalStorageService


class DocumentService:
    """Business logic for document lifecycle and persistence."""

    def __init__(self, db: Session):
        self.db = db

        self.document_repository = DocumentRepository(db)

        self.storage = LocalStorageService(
            base_path=settings.storage_path
        )

    def ingest_document(
        self,
        filename: str,
        content_type: str,
        file_content: bytes,
    ) -> Document:

        if not file_content:
            raise ValueError(
                "Uploaded file is empty."
            )

        checksum = hashlib.sha256(
            file_content
        ).hexdigest()

        logger.info(
            "Starting document ingestion: filename=%s size=%d",
            filename,
            len(file_content),
        )

        existing_document = (
            self.document_repository.get_by_checksum(
                checksum
            )
        )

        if existing_document:
            raise ValueError(
                "A document with this content already exists."
            )

        storage_path = None

        try:
            # 1. Store original file
            storage_path = self.storage.save(
                file_content=file_content,
                filename=filename,
            )

            # 2. Create document record
            document = Document(
                filename=filename,
                content_type=content_type,
                file_size=len(file_content),
                storage_path=storage_path,
                checksum=checksum,
                status="READY",
                version=1,
            )

            self.document_repository.create(
                document
            )

            self.db.commit()
            logger.info(
                "Document ingestion completed: filename=%s document_id=%s",
                filename,
                document.id,
            )
            self.db.refresh(document)

            return document

        except Exception:
            self.db.rollback()

            logger.exception(
                "Document ingestion failed: filename=%s",
                filename,
            )

            if storage_path:
                self.storage.delete(
                    storage_path
                )

            raise