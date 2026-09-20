import logging
import re
from pathlib import Path
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.models.ingestion import IngestionChunk, IngestionRun
from app.repositories.ingestion_repository import IngestionRepository
from app.services.chunker_service import DocumentChunker, TextChunk
from app.services.parser_service import ParserFactory
from app.services.storage_service import SharedDocumentStorage

logger = logging.getLogger(__name__)


class IngestionService:
    def __init__(self, db: Session):
        self.repository = IngestionRepository(db)
        self.db = db
        self.storage = SharedDocumentStorage(settings.document_storage_path)
        self.parser_factory = ParserFactory()
        self.chunker = DocumentChunker(settings.chunk_size, settings.chunk_overlap)

    def ingest(self, document_id: UUID) -> IngestionRun:
        existing = self.repository.get_run(str(document_id), settings.processing_version)
        if existing and existing.status == "COMPLETED":
            logger.info("Returning completed ingestion: document_id=%s", document_id)
            return existing
        if existing and existing.status == "PROCESSING":
            raise RuntimeError("Document ingestion is already in progress.")

        path, file_content = self.storage.read(document_id)
        filename = path.name
        content_type = self._content_type(path)
        run = existing or IngestionRun(
            document_id=str(document_id),
            status="RECEIVED",
            processing_version=settings.processing_version,
            source_filename=filename,
            content_type=content_type,
        )
        if existing is None:
            self.repository.create_run(run)
        run.status = "PROCESSING"
        run.error_message = None
        self.db.commit()
        logger.info("Ingestion requested: document_id=%s", document_id)

        try:
            parser = self.parser_factory.select(filename, content_type)
            logger.info("Parser selected: document_id=%s parser=%s", document_id, type(parser).__name__)
            parsed = parser.parse(file_content, filename, content_type)
            cleaned = self.clean_text(parsed.text)
            logger.info("Text cleaning completed: document_id=%s", document_id)
            chunks = self.chunker.chunk(
                cleaned,
                [
                    (page_number, self.clean_text(page_content))
                    for page_number, page_content in parsed.page_text
                ],
            )
            if not chunks:
                raise ValueError("Document contains no extractable text.")
            self.repository.delete_chunks(run.id)
            self.repository.create_chunks(
                [
                    self._to_model(
                        run,
                        document_id,
                        index,
                        chunk,
                        filename,
                        content_type,
                    )
                    for index, chunk in enumerate(chunks)
                ]
            )
            run.chunk_count = len(chunks)
            run.status = "COMPLETED"
            self.db.commit()
            self.db.refresh(run)
            logger.info("Ingestion completed: document_id=%s chunk_count=%d", document_id, len(chunks))
            return run
        except Exception as exc:
            self.db.rollback()
            run = self.repository.get_run(str(document_id), settings.processing_version)
            if run is not None:
                run.status = "FAILED"
                run.error_message = str(exc)[:1000]
                self.db.commit()
            logger.exception("Ingestion failed: document_id=%s", document_id)
            raise

    @staticmethod
    def clean_text(text: str) -> str:
        lines = [re.sub(r"[ \t]+", " ", line).strip() for line in text.splitlines()]
        paragraphs: list[str] = []
        current: list[str] = []
        for line in lines:
            if line:
                current.append(line)
            elif current:
                paragraphs.append(" ".join(current))
                current = []
        if current:
            paragraphs.append(" ".join(current))
        return "\n\n".join(paragraphs).strip()

    @staticmethod
    def _content_type(path: Path) -> str:
        return {
            ".pdf": "application/pdf",
            ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        }.get(path.suffix.lower(), "application/octet-stream")

    @staticmethod
    def _to_model(
        run: IngestionRun,
        document_id: UUID,
        chunk_index: int,
        chunk: TextChunk,
        filename: str,
        content_type: str,
    ) -> IngestionChunk:
        return IngestionChunk(
            ingestion_run_id=run.id,
            document_id=str(document_id),
            chunk_index=chunk_index,
            content=chunk.content,
            character_count=chunk.character_count,
            token_count=chunk.token_count,
            page_number=chunk.page_number,
            source_filename=filename,
            content_type=content_type,
            metadata_json={"processing_version": settings.processing_version},
        )
