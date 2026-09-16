import hashlib
import uuid

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.models.document import Document
from app.db.models.document_chunk import DocumentChunk
from app.repositories.chunk_repository import ChunkRepository
from app.repositories.document_repository import DocumentRepository
from app.services.chunker_service import DocumentChunkerService
from app.services.parser_service import DocumentParserService
from app.services.storage_service import LocalStorageService


class DocumentService:
    """Business logic for document ingestion."""

    def __init__(self, db: Session):
        self.db = db

        self.document_repository = DocumentRepository(db)
        self.chunk_repository = ChunkRepository(db)

        self.storage = LocalStorageService()
        self.parser = DocumentParserService()
        self.chunker = DocumentChunkerService()

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
                status="PROCESSING",
                version=1,
            )

            self.document_repository.create(
                document
            )

            # 3. Parse
            text = self.parser.parse(
                file_content=file_content,
                filename=filename,
            )

            if not text.strip():
                raise ValueError(
                    "No text could be extracted from the document."
                )

            # 4. Chunk
            chunks = self.chunker.chunk(text)

            if not chunks:
                raise ValueError(
                    "Document produced no chunks."
                )

            # 5. Persist chunks
            chunk_models = [
                DocumentChunk(
                    document_id=document.id,
                    chunk_index=index,
                    content=chunk,
                    token_count=None,
                )
                for index, chunk in enumerate(chunks)
            ]

            self.chunk_repository.create_many(
                chunk_models
            )

            # 6. Mark document ready
            document.status = "READY"

            self.db.commit()
            self.db.refresh(document)

            return document

        except Exception:
            self.db.rollback()

            if storage_path:
                self.storage.delete(
                    storage_path
                )

            raise